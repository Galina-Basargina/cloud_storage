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

    def execute(self, query: str, *args) -> None:
        cur = self.__conn.cursor()
        if isinstance(args, tuple) and len(args) == 1 and isinstance(args[0], dict):
            cur.execute(query, args[0])
        else:
            cur.execute(query, args)
        cur.close()

    def fetch_one(self, query: str, *args) -> typing.Any:
        cur = self.__conn.cursor()
        if isinstance(args, tuple) and len(args) == 1 and isinstance(args[0], dict):
            cur.execute(query, args[0])
        else:
            cur.execute(query, args)
        row = cur.fetchone()
        cur.close()
        return row

    def fetch_all(self, query: str, *args) -> typing.Any:
        cur = self.__conn.cursor()
        if isinstance(args, tuple) and len(args) == 1 and isinstance(args[0], dict):
            cur.execute(query, args[0])
        else:
            cur.execute(query, args)
        row = cur.fetchall()
        cur.close()
        return row

    def commit(self) -> None:
        self.__conn.commit()

    def rollback(self) -> None:
        self.__conn.rollback()
