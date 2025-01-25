from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import argparse
import psycopg2
import typing


def database_execute(conn, query: str) -> None:
    cur = conn.cursor()
    cur.execute(query)
    cur.close()


def database_fetch_one(conn, query: str) -> typing.Any:
    cur = conn.cursor()
    cur.execute(query)
    row = cur.fetchone()
    cur.close()
    return row


def database_connect(settings):
    conn = psycopg2.connect(
        dbname=settings["dbname"],
        user=settings["user"],
        password=settings["password"],
        host=settings["host"],
        port=settings["port"])
    database_execute(conn, f"SET search_path TO {settings['schema']}")
    return conn


def database_disconnect(conn) -> None:
    if not conn.cursor().closed:
        conn.cursor().close()
    conn.close()
    del conn


class HttpGetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        message = f"Cloud access to files v1.0"
        self.wfile.write(bytes(message, "utf8"))


def run(address: str, port: int, server_class=HTTPServer, handler_class=HttpGetHandler):
    server_address = (address, port)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


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
    conn = database_connect(settings)
    version = database_fetch_one(conn, "SELECT version();")
    print(f"Database connected: {version}")

    print(f"Running server at {args.address}:{args.port}")
    run('' if args.address == '*' else args.address, int(args.port))
    print(f"Server stopped")

    database_disconnect(conn)
    print(f"Database disconnected")
