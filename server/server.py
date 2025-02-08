import os
import argparse
from serve import DatabaseInterface, CloudServerRunner


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path} is not a valid path")


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
    parser.add_argument('--storage', help="Files storage", dest="storage", type=dir_path)
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
    cloud = CloudServerRunner(
        address='' if args.address == '*' else args.address,
        port=int(args.port),
        database=db,
        storage=args.storage)
    del cloud
    print(f"Server stopped")

    db.disconnect()
    del db
    print(f"Database disconnected")
