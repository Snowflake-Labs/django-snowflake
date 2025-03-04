import snowflake.connector as snow
from contextlib import contextmanager
from gevent import queue
import time

class SnowflakeConnectionPool:
    def __init__(self, conn_params: dict, maxsize: int = 100, pool_timeout: int = 3600):
        self.maxsize = maxsize
        self.pool = queue.Queue(maxsize=maxsize)
        self.conn_params = conn_params
        self.pool_timeout = pool_timeout

    @contextmanager
    def connection(self):
        conn = self.get()
        try:
            yield conn
        except:
            try:
                conn.close()
            except:
                pass
        finally:
            self.put(conn)
            

    @contextmanager
    def cursor(self):
        with self.connection() as conn:
            cursor = conn.cursor()
            try:
                yield conn.cursor()
            except:
                try:
                    cursor.close()
                except:
                    pass

    def get(self) -> snow.SnowflakeConnection:
        try:
            conn = self.pool.get_nowait()
        except queue.Empty:
            conn = None

        if conn is None:
            conn = self._create_connection()
            conn._pool_timeout = int(time.time()) + self.pool_timeout

        conn._pool = self

        return conn

    def put(self, item: snow.SnowflakeConnection):
        try:
            current_time = int(time.time())
            if item._pool_timeout <= current_time:
                item.close()
            else:
                self.pool.put_nowait(item)
        except queue.Full:
            item.close()

    def _create_connection(self) -> snow.SnowflakeConnection:
        print('creating connection')
        conn = snow.connect(**self.conn_params)
        return conn

    def close(self):
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
            except queue.Empty:
                continue
            try:
                conn.close()
            except Exception:
                continue