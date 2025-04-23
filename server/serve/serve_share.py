import sys
import datetime
import hashlib
import typing
import json
import base64
import binascii
from .database import DatabaseInterface


g_headers_json = {"Content-Type": "application/json"}


def share(server,
          database: DatabaseInterface,
          method: str,
          share_id: typing.Optional[int],
          owner_id: int):
    if method == 'POST' and share_id is None:
        if server.headers.get('Content-Type') != 'application/json':
            response = {'error': 'unsupported Content-Type, use application/json'}
        else:
            content_len = int(server.headers.get('Content-Length'))
            post_body = server.rfile.read(content_len)
            request = json.loads(post_body)
            if request.get('type', 'public') == 'public' and request.get('file_id') is not None:
                file_id: int = int(request.get('file_id'))
                try:
                    database.execute("begin transaction;")
                    row = database.fetch_one(
                        """
insert into shared_files(file,recipient,read_only)
select %(f)s,%(r)s,%(ro)s
where %(f)s not in (select file from shared_files)
returning file;""", {
                            'f': int(file_id),
                            'r': None,
                            'ro': True,
                        })
                    if row:
                        row = database.fetch_one(
                            "select url_filename from files where id=%(f)s;",
                            {'f': int(file_id)})
                    if row is None:
                        database.rollback()
                        response = {'error': 'File not shared'}
                    else:
                        url_filename: str = str(row[0])
                        response = {'message': f'Handled {method} request'}
                        database.commit()
                except:
                    database.rollback()
                    response = {'error': 'File not shared'}
            else:
                response = {'error': 'only public share is supported'}
        error: bool = 'error' in response
        headers = {"Content-Type": "application/json"}
        if not error:
            headers.update({"Location": url_filename})
        server.prepare_response(400 if error else 201,  # Created (=201), Bad request (=400)
                                headers=headers,
                                json_data=response)
    elif method == 'GET' and share_id is None:
        # пока заблокированная возможность
        server.prepare_response(405)
    elif share_id is None:
        # id не указан, требуют или обновить, или удалить ресурс
        server.prepare_response(405)
    elif method == 'GET':
        # пока заблокированная возможность
        server.prepare_response(405)
    elif method == 'PUT':
        # пока заблокированная возможность
        server.prepare_response(405)
    elif method == 'PATCH':
        # пока заблокированная возможность
        server.prepare_response(405)
    elif method == 'DELETE':
        share_found: bool = False
        try:
            row = database.fetch_one("""
with deleted as (
 delete from shared_files where file=%(f)s and recipient is null returning *) 
select count(1) from deleted;""", {'f': share_id})
            share_found: bool = row[0] != 0
        except:
            database.rollback()
            response = {'error': 'Error on shared file delete'}
        else:
            database.commit()
            response = {'message': f'Handled {method} request'}
        error: bool = 'error' in response
        if error:
            server.prepare_response(400, headers=g_headers_json, json_data=response)  # Bad request (=400)
        elif not share_found:
            server.prepare_response(404, headers=g_headers_json, json_data=response)  # Not Found (=404)
        else:
            server.prepare_response(200, headers=g_headers_json, json_data=response)  # OK (=200)
    else:
        # например POST с id (нельзя создать папку, указав id)
        server.prepare_response(405)  # недопустимая комбинация
