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
        schema = settings_dict.get('SCHEMA')
        user = settings_dict.get('USER')
        warehouse = settings_dict.get('WAREHOUSE')
        # snowflake.connector.connect() parameters that have a corresponding
        # snowsql option.
        options = settings_dict['OPTIONS']
        authenticator = options.get('authenticator')
        client_session_keep_alive = options.get('client_session_keep_alive')
        passcode = options.get('passcode')
        passcode_in_password = options.get('passcode_in_password')
        private_key_file = options.get('private_key_file')
        private_key_file_pwd = options.get('private_key_file_pwd')
        role = options.get('role')
        token = options.get('token')

        if account:
            args += ['-a', account]
        if authenticator:
            args += ['--authenticator', authenticator]
        if client_session_keep_alive:
            args += ['--client-session-keep-alive']
        if dbname:
            args += ['-d', dbname]
        if host:
            args += ['-h', host]
        if passcode:
            args += ['--mfa-passcode', passcode]
        if passcode_in_password:
            args += ['--mfa-passcode-in-password']
        if private_key_file:
            args += ['--private-key-path', private_key_file]
        if role:
            args += ['-r', role]
        if schema:
            args += ['-s', schema]
        if token:
            args += ['--token', token]
        if user:
            args += ['-u', user]
        if warehouse:
            args += ['-w', warehouse]

        env = {}
        if password:
            env['SNOWSQL_PWD'] = password
        if private_key_file_pwd:
            env['SNOWSQL_PRIVATE_KEY_PASSPHRASE'] = private_key_file_pwd
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
