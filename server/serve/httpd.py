from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import typing
import json
from .database import DatabaseInterface
from .serve_users import users
from .serve_folders import folders
from .serve_files import files, filedata, filedata_public
from .serve_auth import login, auth, setup_auth_id, logout
from .serve_share import share


class CloudServerRunner:
    def __init__(self, address: str, port: int, database: DatabaseInterface, storage: str):
        self.database: DatabaseInterface = database
        self.__httpd: typing.Optional[HTTPServer] = None
        self.storage: str = storage

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
                         json_data: typing.Optional[typing.Dict[str, typing.Any]] = None,
                         text_message: typing.Optional[str] = None,
                         bytes_data: typing.Optional[bytes] = None):
        self.send_response(code)  # Created (=201), Bad request (=400)
        if headers:
            for key, val in headers.items():
                self.send_header(key, val)
        self.end_headers()
        if json_data:
            string = json.dumps(json_data)
            self.wfile.write(bytes(string, "utf8"))
        elif text_message:
            self.wfile.write(bytes(text_message, "utf8"))
        elif bytes_data is not None:
            self.wfile.write(bytes_data)

    def serve_request(self):
        request_path: str = self.path
        method: str = self.command.upper()
        # не защищенные запросы
        if request_path == '/auth/login':
            login(self, self.runner.database, method)
        elif request_path == '/users':
            users(self, self.runner.database, method, None)
        elif request_path == '/auth/logout':
            logout(self, self.runner.database)
        # защищенные запросы
        else:
            authorized_id: typing.Optional[int] = auth(self, self.runner.database)
            if authorized_id is None:
                if method in ["GET", "HEAD"] and request_path[:10] == '/filedata/':
                    filedata_public(self, self.runner.database, method, request_path)
                else:
                    self.prepare_response(
                        401,  # Unauthorized (=401)
                        headers={"Content-Type": "application/json"},
                        json_data={'error': 'unauthorized'})
            else:
                setup_auth_id(self.runner.database, authorized_id)
                if request_path == '/users/me':
                    users(self, self.runner.database, method, user_id=authorized_id)
                elif request_path == '/folders':
                    folders(self, self.runner.database, method, folder_id=None, owner_id=authorized_id)
                elif request_path[:9] == '/folders/':
                    folders(self, self.runner.database, method, int(request_path[9:]), owner_id=authorized_id)
                elif request_path == '/files':
                    files(self, self.runner.database, self.runner.storage, method=method, file_id=None, owner_id=authorized_id)
                elif request_path[:7] == '/files/':
                    files(self, self.runner.database, self.runner.storage, method, int(request_path[7:]), owner_id=authorized_id)
                elif method == "GET" and request_path[:10] == '/filedata/':
                    filedata(self, self.runner.database, request_path, owner_id=authorized_id)
                elif request_path == '/share':
                    share(self, self.runner.database, method, share_id=None, owner_id=authorized_id)
                elif request_path[:7] == '/share/':
                    share(self, self.runner.database, method, share_id=int(request_path[7:]), owner_id=authorized_id)
                else:
                    self.prepare_response(404)  # Not Found (=404)

    def serve_get(self):
        request_path: str = self.path
        if request_path == '/favicon.ico':
            self.prepare_response(200)
            return
        elif request_path == '/':
            self.prepare_response(200,
                                  headers={"Content-Type": "text/html"},
                                  text_message="Cloud access to files v1.0")
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
