import typing
import json
from .database import DatabaseInterface


g_headers_json = {"Content-Type": "application/json"}


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
            if 'parent' in request and request['parent'] is not None and 'name' in request:
                try:
                    row = database.fetch_one(
                        "insert into folders(parent,owner,name)"
                        "select %(p)s,%(o)s,%(n)s "
                        "where"
                        " %(o)s in (select owner from folders where id=%(p)s) and"
                        " (select id from folders where parent=%(p)s and name=%(n)s) is null "
                        "returning id;", {
                            'p': request['parent'],
                            'o': int(owner_id),
                            'n': request['name'],
                        })
                    if row is None:
                        database.rollback()
                        response = {'error': 'Folder not created'}
                    else:
                        folder_id: int = int(row[0])
                        response = {'message': f'Handled {method} request'}
                        database.commit()
                except:
                    database.rollback()
                    response = {'error': 'Folder not created'}
            else:
                response = {'error': 'unsupported request, use name and parent id'}
        error: bool = 'error' in response
        headers = {"Content-Type": "application/json"}
        if not error:
            headers.update({"Location": f"/folders/{folder_id}"})
        server.prepare_response(400 if error else 201,  # Created (=201), Bad request (=400)
                                headers=headers,
                                json_data=response)
    elif method == 'GET' and folder_id is None:
        try:
            rows = database.fetch_all("""
select id,parent,owner,name
from folders
where %(o)s=owner;""", {'o': int(owner_id)})
            dirs = []
            if rows is not None:
                dirs = [{"id": _[0], "parent": _[1], "owner": _[2], "name": _[3]} for _ in rows]
            response = {'message': f'Handled {method} request', 'folders': dirs}
        except:
            response = {'error': 'Error on folders select'}
        error: bool = 'error' in response
        server.prepare_response(400 if error else 200, headers=g_headers_json, json_data=response)  # OK (=200), Bad request (=400)
    elif folder_id is None:
        # id не указан, требуют или обновить, или удалить ресурс
        server.prepare_response(405)
    elif method == 'GET':
        folder_found: bool = False
        try:
            row = database.fetch_one(
                """
select parent,owner,name
from folders
where id=%(id)s and owner=%(o)s;""", {'id': folder_id, 'o': int(owner_id)})
            response = {'message': f'Handled {method} request'}
            if row is not None:
                folder_found = True
                response.update({'parent': row[0], 'owner': row[1], 'name': row[2]})
        except:
            response = {'error': 'Error on folder select'}
        error: bool = 'error' in response
        if error:
            server.prepare_response(400, headers=g_headers_json, json_data=response)  # Bad request (=400)
        elif not folder_found:
            server.prepare_response(404, headers=g_headers_json, json_data=response)  # Not Found (=404)
        else:
            server.prepare_response(200, headers=g_headers_json, json_data=response)  # OK (=200)
    elif method == 'PUT':
        not_found: bool = True
        if server.headers.get('Content-Type') != 'application/json':
            response = {'error': 'unsupported Content-Type, use application/json'}
        else:
            content_len = int(server.headers.get('Content-Length'))
            post_body = server.rfile.read(content_len)
            request = json.loads(post_body)
            if 'parent' in request and request['parent'] is not None and 'name' in request:
                try:
                    row = database.fetch_one(
                        "update folders set"
                        " parent=%(p)s,"
                        " name=%(n)s"
                        "where id=%(id)s and owner=%(o)s "
                        "returning id;", {
                            'p': request['parent'],
                            'id': int(folder_id),
                            'n': request['name'],
                            'o': int(owner_id),
                        })
                    if row is None:
                        database.rollback()
                        response = {'error': 'Folder not exist'}
                    else:
                        not_found = False
                        response = {'message': f'Handled {method} request'}
                        database.commit()
                except:
                    database.rollback()
                    response = {'error': 'Folder not updated'}
            else:
                response = {'error': 'unsupported request, use name and parent id'}
        # 200 (OK) or 204 (No Content). Use 404 (Not Found), if ID is not found or invalid
        error: bool = 'error' in response
        if error:
            server.prepare_response(400, headers=g_headers_json, json_data=response)  # Bad request (=400)
        elif not_found:
            server.prepare_response(404, headers=g_headers_json, json_data=response)  # Not Found (=404)
        else:
            server.prepare_response(204, headers=g_headers_json, json_data=response)  # No Content (=204)
    elif method == 'PATCH':
        not_found: bool = True
        if server.headers.get('Content-Type') != 'application/json':
            response = {'error': 'unsupported Content-Type, use application/json'}
        else:
            content_len = int(server.headers.get('Content-Length'))
            post_body = server.rfile.read(content_len)
            request = json.loads(post_body)
            # query: typing.List[str] = []
            command: str = ""

            if request.get('parent') and request.get('name'):
                command: str = """
update folders set
 parent=%(p)s,
 name=%(n)s
where
 id=%(id)s and
 owner=%(o)s and
 (select name from folders where parent=%(p)s and name=%(n)s) is null
returning id;"""
            elif request.get('parent'):
                command: str = """
update folders set parent=%(p)s
where
 id=%(id)s and
 owner=%(o)s and
 (select id from folders
  where
   parent=%(p)s and
   name=(select name from folders where id=%(id)s)
 ) is null
returning id;"""
            elif request.get('name'):
                command: str = """
update folders set name=%(n)s
where
 id=%(id)s and
 owner=%(o)s and
 (select name from folders
  where
   name=%(n)s and
   parent=(select parent from folders where id=%(id)s)
 ) is null
returning id;"""


            # if 'parent' in request and request['parent'] is not None:
            #     query.append("parent=%(p)s")
            # if 'name' in request:
            #     query.append("name=%(n)s")
            if command != "":
                try:
                    row = database.fetch_one(
                        # f"update folders set {','.join(query)} "
                        # "where id=%(id)s and owner=%(o)s "
                        # "returning id;",
                        command, {
                            'p': request.get('parent'),
                            'id': int(folder_id),
                            'n': request.get('name'),
                            'o': int(owner_id),
                        })
                    if row is None:
                        database.rollback()
                        response = {'error': 'Folder not exist'}
                    else:
                        not_found = False
                        response = {'message': f'Handled {method} request'}
                        database.commit()
                except:
                    database.rollback()
                    response = {'error': 'Folder not updated'}
            else:
                response = {'error': 'unsupported request, use name or parent id'}
        # 200 (OK) or 204 (No Content). Use 404 (Not Found), if ID is not found or invalid
        error: bool = 'error' in response
        if error:
            server.prepare_response(400, headers=g_headers_json, json_data=response)  # Bad request (=400)
        elif not_found:
            server.prepare_response(404, headers=g_headers_json, json_data=response)  # Not Found (=404)
        else:
            server.prepare_response(204, headers=g_headers_json, json_data=response)  # No Content (=204)
    elif method == 'DELETE':
        folder_found: bool = False
        try:
            folders_select: str = """
with recursive r(id) as (
 select id,parent from folders 
 where
  id=%(id)s and 
  parent is not null and -- except root folder
  owner=%(o)s
union 
 select f.id,f.parent from folders f
 join r on (f.parent=r.id)
)
select id from r
"""
            database.execute(f"""
delete from files where folder in ({folders_select});""",
                {'id': folder_id, 'o': int(owner_id)})
            row = database.fetch_one(f"""
with deleted as (
 delete from folders where id in ({folders_select}) returning *
) 
select count(1) from deleted;""", {'id': folder_id, 'o': int(owner_id)})
            folder_found: bool = row[0] != 0
        except:
            database.rollback()
            response = {'error': 'Error on folder delete'}
        else:
            database.commit()
            response = {'message': f'Handled {method} request'}
        error: bool = 'error' in response
        if error:
            server.prepare_response(400, headers=g_headers_json, json_data=response)  # Bad request (=400)
        elif not folder_found:
            server.prepare_response(404, headers=g_headers_json, json_data=response)  # Not Found (=404)
        else:
            server.prepare_response(200, headers=g_headers_json, json_data=response)  # OK (=200)
    else:
        # например POST с id (нельзя создать папку, указав id)
        server.prepare_response(405)  # недопустимая комбинация
