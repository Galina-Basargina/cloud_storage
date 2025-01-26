from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import argparse
import typing
import json
from database import DatabaseInterface


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

    def prepare_response(self,
                         code: int,
                         headers: typing.Optional[typing.Dict[str, str]] = None,
                         data: typing.Optional[typing.Dict[str, typing.Any]] = None,
                         message: typing.Optional[str] = None):
        self.send_response(code)  # Created (=201), Bad request (=400)
        if headers:
            for key, val in headers.items():
                self.send_header(key, val)
        self.end_headers()
        if data:
            string = json.dumps(data)
            self.wfile.write(bytes(string, "utf8"))
        if message:
            self.wfile.write(bytes(message, "utf8"))

    def serve_request(self):
        request_path: str = self.path
        method: str = self.command.upper()
        if request_path == '/users':
            self.serve_users(self, self.runner.database, method, None)
        if request_path[:7] == '/users/':
            self.serve_users(self, self.runner.database, method, int(request_path[7:]))

    def serve_get(self):
        request_path: str = self.path
        if request_path == '/favicon.ico':
            self.prepare_response(200)
            return
        elif request_path == '/':
            self.prepare_response(200,
                                  headers={"Content-Type": "text/html"},
                                  message="Cloud access to files v1.0")
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
