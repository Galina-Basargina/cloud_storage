from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import argparse
from pyexpat.errors import messages


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
    args = parser.parse_args()

    print(f"Running server at {args.address}:{args.port}")

    run('' if args.address == '*' else args.address, int(args.port))
