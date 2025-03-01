import typing
import json
import hashlib
from .database import DatabaseInterface


g_headers_json = {"Content-Type": "application/json"}


def login(server, database: DatabaseInterface, method: str) -> None:
    if method == 'POST':
        if server.headers.get('Content-Type') != 'application/json':
            response = {'error': 'unsupported Content-Type, use application/json'}
        else:
            content_len = int(server.headers.get('Content-Length'))
            post_body = server.rfile.read(content_len)
            request = json.loads(post_body)
            if 'login' in request and 'password' in request:
                try:
                    database.execute("begin transaction;")  # для выполнения одновременно нескольких действий
                    database.execute("delete from auth where (current_timestamp - logged_at) > interval '24 hours';")
                    checksum: str = hashlib.md5(request["password"].encode("utf-8")).hexdigest()
                    row = database.fetch_one("""
select id,current_timestamp
from users
where login=%(l)s and password_checksum=%(p)s;""", {'l': request['login'], 'p': checksum})
                    if row is None:
                        response = {'error': 'unauthorized'}
                    else:
                        id: int = int(row[0])
                        salt: str = str(row[1])  # добавление случайных кусочков в токен (посолить)
                        token: str = f"{request['login']}:{checksum}:{salt}"
                        token: str = hashlib.sha256(token.encode("utf-8")).hexdigest()
                        database.execute(
                            "insert into auth (logged_in,access_token) values(%(id)s,%(t)s);",
                            {'id': id, 't': token})
                        response = {'token': token}
                except:
                    database.rollback()
                    response = {'error': 'unauthorized'}
                else:
                    database.commit()
            else:
                response = {'error': 'unauthorized'}
        error: bool = 'error' in response
        server.prepare_response(401 if error else 200,  # OK (=200), Unauthorized (=401)
                                headers=g_headers_json,
                                json_data=response)
    else:
        # все остальные типы запросов недопустимы при авторизации
        server.prepare_response(405)  # недопустимая комбинация


def auth(server, database: DatabaseInterface) -> typing.Optional[int]:
    bearer: typing.Optional[str] = server.headers.get('Authorization')
    if bearer is None:
        return None
    if bearer[:7] != "Bearer ":
        return None
    try:
        database.execute("begin transaction;")  # для выполнения одновременно нескольких действий
        token: str = bearer[7:]
        database.execute("""
delete from auth
where (current_timestamp - logged_at) > interval '24 hours' and access_token=%(t)s;""",
            {'t': token})
        row = database.fetch_one("""
select logged_in from auth
where access_token=%(t)s;""",
            {'t': token})
        database.commit()
        if row is None:
            return None
        return int(row[0])
    except:
        database.rollback()
        return None


def setup_auth_id(database: DatabaseInterface, authorized_id: int) -> None:
    database.execute("SET cloud_storage.auth_id=%(id)s", {'id': authorized_id})


def logout(server, database: DatabaseInterface) -> None:
    bearer: typing.Optional[str] = server.headers.get('Authorization')
    if bearer is None:
        return
    if bearer[:7] != "Bearer ":
        return
    try:
        token: str = bearer[7:]
        database.execute("""
delete from auth
where access_token=%(t)s;""", {'t': token})
    except:
        database.rollback()
    else:
        database.commit()
    server.prepare_response(200)  # OK (=200)
