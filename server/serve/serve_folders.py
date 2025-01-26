import typing
import json
from .database import DatabaseInterface


def folders(server,
            database: DatabaseInterface,
            method: str,
            folder_id: typing.Optional[int],
            owner_id: int):
    if method == 'POST' and folder_id is None:
        if server.headers.get('Content-Type') != 'application/json':
            response = {'error': 'unsupported Content-Type, use application/json'}
        else:
            content_len = int(server.headers.get('Content-Length'))
            post_body = server.rfile.read(content_len)
            request = json.loads(post_body)
            if 'parent' in request and 'name' in request:
                try:
                    row = database.fetch_one(
                        "insert into folders(parent,owner,name)"
                        "values(%(p)s,%(o)s,%(n)s)"
                        "returning id;", {
                            'p': request['parent'],
                            'o': int(owner_id),
                            'n': request['name'],
                        })
                except:
                    database.rollback()
                    response = {'error': 'Folder not created'}
                else:
                    folder_id: int = int(row[0])
                    database.commit()
                    response = {'message': f'Handled {method} request'}
            else:
                response = {'error': 'unsupported request, use name and parent id'}
        error: bool = 'error' in response
        headers = {"Content-Type": "application/json"}
        if not error:
            headers.update({"Location": f"/folders/{folder_id}"})
        server.prepare_response(400 if error else 201,  # Created (=201), Bad request (=400)
                                headers=headers,
                                data=response)
    elif method == 'GET' and folder_id is None:
        try:
            rows = database.fetch_all("select id,parent,owner,name from folders;")
            dirs = []
            if rows is not None:
                dirs = [{"id": _[0], "parent": _[1], "owner": _[2], "name": _[3]} for _ in rows]
            response = {'message': f'Handled {method} request', 'folders': dirs}
        except:
            response = {'error': 'Error on folders select'}
        error: bool = 'error' in response
        server.prepare_response(400 if error else 200, data=response)  # OK (=200), Bad request (=400)
    elif folder_id is None:
        # id не указан, требуют или обновить, или удалить ресурс
        server.prepare_response(405)
    elif method == 'GET':
        folder_found: bool = False
        try:
            row = database.fetch_one(
                "select parent,owner,name from folders where id=%(id)s;",
                {'id': folder_id})
            response = {'message': f'Handled {method} request'}
            if row is not None:
                folder_found = True
                response.update({'parent': row[0], 'owner': row[1], 'name': row[2]})
        except:
            response = {'error': 'Error on folder select'}
        error: bool = 'error' in response
        if error:
            server.prepare_response(400, data=response)  # Bad request (=400)
        elif not folder_found:
            server.prepare_response(404, data=response)  # Not Found (=404)
        else:
            server.prepare_response(200, data=response)  # OK (=200)
    elif method == 'PUT':
        # 200 (OK) or 204 (No Content). Use 404 (Not Found), if ID is not found or invalid
        server.prepare_response(405)  # недопустимая комбинация
    elif method == 'PATCH':
        # 200 (OK) or 204 (No Content). Use 404 (Not Found), if ID is not found or invalid
        server.prepare_response(405)  # недопустимая комбинация
    elif method == 'DELETE':
        folder_found: bool = False
        try:
            row = database.fetch_one(
                "with deleted as (delete from folders where id=%(id)s returning *) "
                "select count(1) from deleted;", {'id': folder_id})
            folder_found: bool = row[0] == 1
        except:
            database.rollback()
            response = {'error': 'Error on folder delete'}
        else:
            database.commit()
            response = {'message': f'Handled {method} request'}
        error: bool = 'error' in response
        if error:
            server.prepare_response(400, data=response)  # Bad request (=400)
        elif not folder_found:
            server.prepare_response(404, data=response)  # Not Found (=404)
        else:
            server.prepare_response(200, data=response)  # OK (=200)
    else:
        # например POST с id (нельзя создать папку, указав id)
        server.prepare_response(405)  # недопустимая комбинация
