from http.cookiejar import request_path
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import argparse
import psycopg2
import typing
import json


class DatabaseInterface:
    def __init__(self, settings):
        self.__conn = None
        self.settings = settings

    def connect(self):
        self.__conn = psycopg2.connect(
            dbname=self.settings["dbname"],
            user=self.settings["user"],
            password=self.settings["password"],
            host=self.settings["host"],
            port=self.settings["port"])
        self.execute(f"SET search_path TO {self.settings['schema']}")

    def disconnect(self) -> None:
        if not self.__conn.cursor().closed:
            self.__conn.cursor().close()
        self.__conn.close()
        del self.__conn
        self.__conn = None

    def execute(self, query: str) -> None:
        cur = self.__conn.cursor()
        cur.execute(query)
        cur.close()

    def fetch_one(self, query: str) -> typing.Any:
        cur = self.__conn.cursor()
        cur.execute(query)
        row = cur.fetchone()
        cur.close()
        return row

    def commit(self) -> None:
        self.__conn.commit()

    def rollback(self) -> None:
        self.__conn.rollback()


class CloudServerRunner:
    def __init__(self, address: str, port: int, database: DatabaseInterface):
        self.database: DatabaseInterface = database
        self.__httpd: typing.Optional[HTTPServer] = None

        def handler(*args):
            CloudServer(self, *args)

        self.__httpd = HTTPServer((address, port), handler)
        try:
            self.__httpd.serve_forever()
        except KeyboardInterrupt:
            self.stop()

    def __del__(self):
        self.stop()

    def stop(self):
        if self.__httpd:
            self.__httpd.server_close()
            del self.__httpd
            self.__httpd = None


class CloudServer(BaseHTTPRequestHandler):
    def __init__(self, runner: CloudServerRunner, *args):
        self.runner: CloudServerRunner = runner
        BaseHTTPRequestHandler.__init__(self, *args)

    def serve_users(self, method: str, user_id: typing.Optional[int]):
        if method == 'POST' and user_id is None:
            if self.headers.get('Content-Type') != 'application/json':
                response = {'error': 'unsupported Content-Type, use application/json'}
            else:
                content_len = int(self.headers.get('Content-Length'))
                post_body = self.rfile.read(content_len)
                request = json.loads(post_body)
                if 'login' in request and 'password_checksum' in request:
                    try:
                        row = self.runner.database.fetch_one(
                            "insert into users(login, password_checksum) "
                            f"values('{request['login']}', '{request['password_checksum']}') "
                            "returning id;")
                    except:
                        self.runner.database.rollback()
                        response = {'error': 'User not created'}
                    else:
                        user_id: int = int(row[0])
                        self.runner.database.commit()
                        response = {'message': f'Handled {method} request'}
                else:
                    response = {'error': 'unsupported request, use login'}
            error: bool = 'error' in response
            self.send_response(400 if error else 201)  # Created (=201), Bad request (=400)
            self.send_header("Content-Type", "application/json")
            if not error:
                self.send_header("Location", f"/users/{user_id}")
            self.end_headers()
            message = json.dumps(response)
            self.wfile.write(bytes(message, "utf8"))
        elif method == 'GET' and user_id is None:
            pass
        elif user_id is None:
            # id не указан, требуют или обновить, или удалить ресурс
            self.send_response(405)  # метод не разрешен
            self.end_headers()
        elif method == 'GET':
            pass
        elif method == 'PUT':
            pass
        elif method == 'PATCH':
            pass
        elif method == 'DELETE':
            pass
        else:
            # например POST с id (нельзя создать пользователя, указав id)
            self.send_response(405)  # недопустимая комбинация
            self.end_headers()

    def serve_request(self):
        request_path: str = self.path
        method: str = self.command.upper()
        if request_path == '/users':
            self.serve_users(method, None)
        if request_path[:7] == '/users/':
            self.serve_users(method, int(request_path[7:]))

    def serve_get(self):
        request_path: str = self.path
        if request_path == '/favicon.ico':
            self.send_response(200)
            self.end_headers()
            return
        elif request_path == '/':
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            message = f"Cloud access to files v1.0"
            self.wfile.write(bytes(message, "utf8"))
            return
        self.serve_request()

    def serve_post(self):
        self.serve_request()

    def serve_options(self):
        self.serve_request()

    # ПОДРОБНЕЕ СМОТРИ ТУТ: https://restfulapi.net/http-methods/
    do_GET = serve_get  # прочитать данные (получить файлы)
    do_HEAD = serve_get
    do_POST = serve_post  # создать ресурс (создать файл, папку, пользователя)
    do_DELETE = serve_post  # удалить ресурс
    do_PUT = serve_post  # обновить/заменить (заменить существующий файл без пересоздания)
    do_PATCH = serve_post  # частичная замена/редактирование (отредактировать файл или настроить папку, пользователя)
    do_OPTIONS = serve_options


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='cloud server',
        description='Cloud access to files',
        epilog='python3 server.py --address=127.0.0.1 --port=8080')
    parser.add_argument('-a', '--address', help="Server address", default='*', dest="address")
    parser.add_argument('-p', '--port', help="HTTP port", default=8080, dest="port")
    parser.add_argument('--dbname', help="Database name", default="postgres", dest="dbname")
    parser.add_argument('--dbuser', help="Database user", default="postgres", dest="dbuser")
    parser.add_argument('--dbpassword', help="Database password", default="password", dest="dbpassword")
    parser.add_argument('--dbhost', help="Database host", default="localhost", dest="dbhost")
    parser.add_argument('--dbport', help="Database port", default="5432", dest="dbport")
    parser.add_argument('--dbschema', help="Database schema", default="public", dest="dbschema")
    args = parser.parse_args()

    settings = {
        'dbname': args.dbname,
        'user': args.dbuser,
        'password': args.dbpassword,
        'host': args.dbhost,
        'port': args.dbport,
        'schema': args.dbschema}
    db: DatabaseInterface = DatabaseInterface(settings)
    db.connect()
    version = db.fetch_one("SELECT version();")
    print(f"Database connected: {version}")

    print(f"Running server at {args.address}:{args.port}")
    cloud = CloudServerRunner(
        address='' if args.address == '*' else args.address,
        port=int(args.port),
        database=db)
    del cloud
    print(f"Server stopped")

    db.disconnect()
    del db
    print(f"Database disconnected")
