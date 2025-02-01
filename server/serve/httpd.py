from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import typing
import json
from .database import DatabaseInterface
from .serve_users import users
from .serve_folders import folders
from .serve_auth import login, auth


class CloudServerRunner:
    def __init__(self, address: str, port: int, database: DatabaseInterface):
        self.database: DatabaseInterface = database
        self.__httpd: typing.Optional[HTTPServer] = None

        def handler(*args):
            return CloudServer(self, *args)

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
        # не защищенные запросы
        if request_path == '/auth/login':
            login(self, self.runner.database, method)
        elif request_path == '/users':
            users(self, self.runner.database, method, None)
        # защищенные запросы
        else:
            authorized_id: typing.Optional[int] = auth(self, self.runner.database)
            if authorized_id is None:
                self.prepare_response(
                    401,  # Unauthorized (=401)
                    headers={"Content-Type": "application/json"},
                    data={'error': 'unauthorized'})
            elif request_path == '/users/me':
                users(self, self.runner.database, method, user_id=authorized_id)
            elif request_path == '/folders':
                folders(self, self.runner.database, method, None, owner_id=authorized_id)
            elif request_path[:9] == '/folders/':
                folders(self, self.runner.database, method, int(request_path[9:]), owner_id=authorized_id)

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
