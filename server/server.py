from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import argparse
import psycopg2
import typing


class DatabaseInterface:
    def __init__(self, settings):
        self.__conn = None
        self.settings = settings

    def connect(self):
        self.__conn = psycopg2.connect(
            dbname=self.settings["dbname"],
            user=self.settings["user"],
            password=self.settings["password"],
            host=self.settings["host"],
            port=self.settings["port"])
        self.execute(f"SET search_path TO {self.settings['schema']}")

    def disconnect(self) -> None:
        if not self.__conn.cursor().closed:
            self.__conn.cursor().close()
        self.__conn.close()
        del self.__conn
        self.__conn = None

    def execute(self, query: str) -> None:
        cur = self.__conn.cursor()
        cur.execute(query)
        cur.close()

    def fetch_one(self, query: str) -> typing.Any:
        cur = self.__conn.cursor()
        cur.execute(query)
        row = cur.fetchone()
        cur.close()
        return row


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
    db: DatabaseInterface = DatabaseInterface(settings)
    db.connect()
    version = db.fetch_one("SELECT version();")
    print(f"Database connected: {version}")

    print(f"Running server at {args.address}:{args.port}")
    run('' if args.address == '*' else args.address, int(args.port))
    print(f"Server stopped")

    db.disconnect()
    del db
    print(f"Database disconnected")
