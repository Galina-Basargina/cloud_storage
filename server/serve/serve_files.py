import datetime
import hashlib
import typing
import json
from .database import DatabaseInterface


g_headers_json = {"Content-Type": "application/json"}


def files(server,
          database: DatabaseInterface,
          method: str,
          file_id: typing.Optional[int],
          owner_id: int):
    if method == 'POST' and file_id is None:
        if server.headers.get('Content-Type') != 'application/json':
            response = {'error': 'unsupported Content-Type, use application/json'}
        else:
            content_len = int(server.headers.get('Content-Length'))
            post_body = server.rfile.read(content_len)
            request = json.loads(post_body)
            if 'folder' in request and request['folder'] is not None:
                salt: str = datetime.datetime.now().isoformat()
                server_filename: str = f"{request['folder']}:{request['original_filename']}:{salt}"
                server_filename = hashlib.sha256(server_filename.encode("utf-8")).hexdigest()
                check_original_filename: str = ""
                if request.get('original_filename') is not None:
                    check_original_filename: str = \
                        "and (select id from files where folder=%(f)s and original_filename=%(of)s) is null"
                try:
                    row = database.fetch_one(
                        f"""
insert into files("owner",folder,original_filename,server_filename,url_filename,filesize,content_type)
select %(o)s,%(f)s,%(of)s,%(sf)s,%(uf)s,%(fs)s,%(c)s 
where
 %(o)s in (select owner from folders where id=%(f)s)
 {check_original_filename}
returning id;""", {
                            'o': int(owner_id),
                            'f': request['folder'],
                            'of': request.get('original_filename'),  # может быть None
                            'sf': f"/var/lib/cloud_storage/{server_filename}",
                            'uf': f"/filedata/{server_filename}",
                            'fs': int(256),
                            'c': request['content_type'],
                        })
                    if row is None:
                        database.rollback()
                        response = {'error': 'File not created'}
                    else:
                        file_id: int = int(row[0])
                        response = {'message': f'Handled {method} request'}
                        database.commit()
                except:
                    database.rollback()
                    response = {'error': 'File not created'}
            else:
                response = {'error': 'unsupported request, use folder id'}
        error: bool = 'error' in response
        headers = {"Content-Type": "application/json"}
        if not error:
            headers.update({"Location": f"/files/{file_id}"})
        server.prepare_response(400 if error else 201,  # Created (=201), Bad request (=400)
                                headers=headers,
                                data=response)
    elif method == 'GET' and file_id is None:
        try:
            rows = database.fetch_all("""
select id,"owner",folder,original_filename,url_filename,filesize,content_type,upload_date
from files
where %(o)s=owner;""", {'o': int(owner_id)})
            files_list = []
            if rows is not None:
                files_list = [{"id": _[0],
                               "owner": _[1],
                               "folder": _[2],
                               "original_filename": _[3],
                               "url_filename": _[4],
                               "filesize": _[5],
                               "content_type": _[6],
                               "upload_date": str(_[7].isoformat())}
                              for _ in rows]
            response = {'message': f'Handled {method} request', 'files': files_list}
        except:
            response = {'error': 'Error on files select'}
        error: bool = 'error' in response
        server.prepare_response(400 if error else 200, data=response)  # OK (=200), Bad request (=400)
    elif file_id is None:
        # id не указан, требуют или обновить, или удалить ресурс
        server.prepare_response(405)
    elif method == 'GET':
        file_found: bool = False
        try:
            row = database.fetch_one(
                """
select "owner",folder,original_filename,url_filename,filesize,content_type,upload_date
from files
where id=%(id)s and owner=%(o)s;""", {'id': file_id, 'o': int(owner_id)})
            response = {'message': f'Handled {method} request'}
            if row is not None:
                file_found = True
                response.update({'owner': row[0],
                                 'folder': row[1],
                                 'original_filename': row[2],
                                 'url_filename': row[3],
                                 'filesize': row[4],
                                 'content_type': row[5],
                                 'upload_date': str(row[6].isoformat())})
        except:
            response = {'error': 'Error on file select'}
        error: bool = 'error' in response
        if error:
            server.prepare_response(400, data=response)  # Bad request (=400)
        elif not file_found:
            server.prepare_response(404, data=response)  # Not Found (=404)
        else:
            server.prepare_response(200, data=response)  # OK (=200)
    elif method == 'PUT':
        # пока заблокированная возможность
        server.prepare_response(405)
    elif method == 'PATCH':
        not_found: bool = True
        if server.headers.get('Content-Type') != 'application/json':
            response = {'error': 'unsupported Content-Type, use application/json'}
        else:
            content_len = int(server.headers.get('Content-Length'))
            post_body = server.rfile.read(content_len)
            request = json.loads(post_body)
            query: typing.List[str] = []
            if 'folder' in request and request['folder'] is not None:
                query.append("folder=%(f)s")
            if 'original_filename' in request:
                query.append("original_filename=%(of)s")
            if query:
                try:
                    row = database.fetch_one(
                        f"update files set {','.join(query)} "
                        "where id=%(id)s and owner=%(o)s "
                        "returning id;", {
                            'f': request.get('folder'),
                            'of': request.get('original_filename'),
                            'o': int(owner_id),
                            'id': int(file_id),
                        })
                    if row is None:
                        database.rollback()
                        response = {'error': 'File not updated'}
                    else:
                        not_found = False
                        response = {'message': f'Handled {method} request'}
                        database.commit()
                except:
                    database.rollback()
                    response = {'error': 'File not updated'}
            else:
                response = {'error': 'unsupported request, use folder or original_filename'}
        # 200 (OK) or 204 (No Content). Use 404 (Not Found), if ID is not found or invalid
        error: bool = 'error' in response
        if error:
            server.prepare_response(400, g_headers_json, data=response)  # Bad request (=400)
        elif not_found:
            server.prepare_response(404, g_headers_json, data=response)  # Not Found (=404)
        else:
            server.prepare_response(204, g_headers_json, data=response)  # No Content (=204)
    elif method == 'DELETE':
        file_found: bool = False
        try:
            row = database.fetch_one("""
with deleted as (
 delete from files where id=%(id)s and "owner"=%(o)s returning *) 
select count(1) from deleted;""", {'id': file_id, 'o': int(owner_id)})
            file_found: bool = row[0] != 0
        except:
            database.rollback()
            response = {'error': 'Error on file delete'}
        else:
            database.commit()
            response = {'message': f'Handled {method} request'}
        error: bool = 'error' in response
        if error:
            server.prepare_response(400, g_headers_json, data=response)  # Bad request (=400)
        elif not file_found:
            server.prepare_response(404, g_headers_json, data=response)  # Not Found (=404)
        else:
            server.prepare_response(200, g_headers_json, data=response)  # OK (=200)
    else:
        # например POST с id (нельзя создать папку, указав id)
        server.prepare_response(405)  # недопустимая комбинация
