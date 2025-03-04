import snowflake.connector as snow
from contextlib import contextmanager
from gevent import queue

class SnowflakeConnectionPool:
    def __init__(self, conn_params: dict, maxsize: int = 100):
        self.maxsize = maxsize
        self.pool = queue.Queue(maxsize=maxsize)
        self.conn_params = conn_params

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
            conn = self.create_connection()

        conn._pool = self

        return conn

    def put(self, item: snow.SnowflakeConnection):
        try:
            self.pool.put_nowait(item)
        except queue.Full:
            item.close()

    def create_connection(self) -> snow.SnowflakeConnection:
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