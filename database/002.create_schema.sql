-- UTF-8 without BOM
-- скрипт выполняется с правами пользователя cs_user (см. 001.create_db.sql)
-- скрипт создаёт схему базы данных

CREATE SCHEMA IF NOT EXISTS coursework AUTHORIZATION cs_user;

drop table if exists coursework.shares_folders;
drop table if exists coursework.shares_files;
drop table if exists coursework.files;
drop table if exists coursework.folders;
drop table if exists coursework.auth;
drop table if exists coursework.users;


create table coursework.users (
 id serial primary key,
 login text not null unique,
 password_checksum text not null
);

create table coursework.auth (
 logged_in integer not null references coursework.users(id),
 access_token text not null unique
);

create table coursework.folders (
 id serial primary key,
 parent integer null references coursework.folders(id),
 owner integer not null references coursework.users(id),
 name text not null,
 constraint folders_unique unique (parent, name)
);

create table coursework.files (
 id serial primary key,
 owner integer not null references coursework.users(id),
 folder integer null references coursework.folders(id), -- корневая это null
 original_filename text, -- исходное имя файла, если известно
 server_filename text not null unique, -- путь к файлу на сервере (в БД только ссылка)
 url_filename text not null unique, -- уникальное имя файла для веба
 filesize integer not null,
 content_type text not null, -- тип файла для веба
 upload_date timestamp not null default current_timestamp
);

create table coursework.shares_files (
 file integer references coursework.files(id),
 recipient integer references coursework.users(id),
 read_onle bool not null default true -- при false можно удалить, переименовать
);

create table coursework.shares_folders (
 folder integer references coursework.folders(id),
 recipient integer references coursework.users(id),
 read_onle bool not null default true -- при false можно удалить, переименовать
);


