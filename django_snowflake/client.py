import signal

from django.db.backends.base.client import BaseDatabaseClient


class DatabaseClient(BaseDatabaseClient):
    executable_name = 'snowsql'

    @classmethod
    def settings_to_cmd_args_env(cls, settings_dict, parameters):
        args = [cls.executable_name]

        account = settings_dict.get('ACCOUNT')
        dbname = settings_dict.get('NAME')
        host = settings_dict.get('HOST')
        password = settings_dict.get('PASSWORD')
        port = settings_dict.get('PORT')
        role = settings_dict.get('ROLE')
        schema = settings_dict.get('SCHEMA')
        user = settings_dict.get('USER')
        warehouse = settings_dict.get('WAREHOUSE')

        if account:
            args += ['-a', account]
        if dbname:
            args += ['-d', dbname]
        if host:
            args += ['-h', host]
        if port:
            args += ['-p', port]
        if role:
            args += ['-r', role]
        if schema:
            args += ['-s', schema]
        if user:
            args += ['-u', user]
        if warehouse:
            args += ['-w', warehouse]

        env = {}
        if password:
            env['SNOWSQL_PWD'] = password
        return args, (env or None)

    def runshell(self, parameters):
        sigint_handler = signal.getsignal(signal.SIGINT)
        try:
            # Allow SIGINT to pass to snowsql to abort queries.
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            super().runshell(parameters)
        finally:
            # Restore the original SIGINT handler.
            signal.signal(signal.SIGINT, sigint_handler)
