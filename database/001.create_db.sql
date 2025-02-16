-- UTF-8 without BOM
-- скрипт выполняется с правами суперпользователя postgres
-- скрипт создаёт табличные пространства, базу данных, пользователя для работы с новой БД и выдаёт права

DROP DATABASE cs_db;
DROP USER cs_user;

CREATE DATABASE cs_db
    WITH
    --по умолчанию:OWNER = postgres
    ENCODING = 'UTF8'
    --порядок сортировки:LC_COLLATE = 'Russian_Russia.1251'
    --порядок сортировки:LC_CTYPE = 'Russian_Russia.1251'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

--по умолчанию:GRANT ALL ON DATABASE cs_db TO postgres;
--по умолчанию:GRANT TEMPORARY, CONNECT ON DATABASE cs_db TO PUBLIC;

CREATE USER cs_user
    WITH
    LOGIN PASSWORD 'cs_a5Z7dMkmSJb9' -- this is the value you probably need to edit
    NOSUPERUSER
    INHERIT
    NOCREATEDB
    NOCREATEROLE
    NOREPLICATION;

GRANT ALL ON DATABASE cs_db TO cs_user;
