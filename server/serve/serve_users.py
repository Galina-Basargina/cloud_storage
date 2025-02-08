import typing
import json
from .database import DatabaseInterface


g_headers_json = {"Content-Type": "application/json"}


def users(server, database: DatabaseInterface, method: str, user_id: typing.Optional[int]):
    if method == 'POST' and user_id is None:
        if server.headers.get('Content-Type') != 'application/json':
            response = {'error': 'unsupported Content-Type, use application/json'}
        else:
            content_len = int(server.headers.get('Content-Length'))
            post_body = server.rfile.read(content_len)
            request = json.loads(post_body)
            if 'login' in request and 'password_checksum' in request:
                try:
                    database.execute("begin transaction;")  # для выполнения одновременно нескольких действий
                    row = database.fetch_one(
                        "insert into users(login, password_checksum)"
                        f"values(%(login)s, %(pass)s) "
                        "returning id;", {
                            'login': request['login'],
                            'pass': request['password_checksum'],
                        })
                    user_id: int = int(row[0])
                    database.execute(
                        "insert into folders(parent,owner,name) values(null,%(u)s,'');",
                        {'u': user_id})
                except:
                    database.rollback()
                    response = {'error': 'User not created'}
                else:
                    database.commit()
                    response = {'message': f'Handled {method} request'}
            else:
                response = {'error': 'unsupported request, use login'}
        error: bool = 'error' in response
        headers = {"Content-Type": "application/json"}
        if not error:
            headers.update({"Location": f"/users/{user_id}"})
        server.prepare_response(400 if error else 201,  # Created (=201), Bad request (=400)
                                headers=headers,
                                json_data=response)
    elif method == 'GET' and user_id is None:
        try:
            rows = database.fetch_all("select id,login from users;")
            logins = []
            if rows is not None:
                logins = [{"id": _[0], "login": _[1]} for _ in rows]
            response = {'message': f'Handled {method} request', 'users': logins}
        except:
            response = {'error': 'Error on users select'}
        error: bool = 'error' in response
        server.prepare_response(400 if error else 200, g_headers_json, json_data=response)  # OK (=200), Bad request (=400)
    elif user_id is None:
        # id не указан, требуют или обновить, или удалить ресурс
        server.prepare_response(405)
    elif method == 'GET':
        user_found: typing.Optional[str] = None
        try:
            row = database.fetch_one(
                "select login from users where id=%(id)s;",
                {'id': user_id})
            response = {'message': f'Handled {method} request'}
            if row is not None:
                user_found = row[0]
                response.update({'login': user_found})
        except:
            response = {'error': 'Error on user select'}
        error: bool = 'error' in response
        if error:
            server.prepare_response(400, g_headers_json, json_data=response)  # Bad request (=400)
        elif not user_found:
            server.prepare_response(404, g_headers_json, json_data=response)  # Not Found (=404)
        else:
            server.prepare_response(200, g_headers_json, json_data=response)  # OK (=200)
    elif method == 'PUT':
        # 200 (OK) or 204 (No Content). Use 404 (Not Found), if ID is not found or invalid
        server.prepare_response(405)  # недопустимая комбинация
    elif method == 'PATCH':
        # 200 (OK) or 204 (No Content). Use 404 (Not Found), if ID is not found or invalid
        server.prepare_response(405)  # недопустимая комбинация
    elif method == 'DELETE':
        user_found: bool = False
        try:
            database.execute("begin transaction;")  # для выполнения одновременно нескольких действий
            # удалить папки пользователя
            database.execute("delete from folders "
                             "where id in (select id from folders where \"owner\"=%(id)s;",
                             {'id': user_id})
            # удалить пользователя и вернуть строку
            row = database.fetch_one(
                "with deleted as (delete from users where id=%(id)s returning *) "
                "select count(1) from deleted;", {'id': user_id})
            user_found: bool = row[0] == 1
        except:
            database.rollback()
            response = {'error': 'Error on user delete'}
        else:
            database.commit()
            response = {'message': f'Handled {method} request'}
        error: bool = 'error' in response
        if error:
            server.prepare_response(400, g_headers_json, json_data=response)  # Bad request (=400)
        elif not user_found:
            server.prepare_response(404, g_headers_json, json_data=response)  # Not Found (=404)
        else:
            server.prepare_response(200, g_headers_json, json_data=response)  # OK (=200)
    else:
        # например POST с id (нельзя создать пользователя, указав id)
        server.prepare_response(405)  # недопустимая комбинация
