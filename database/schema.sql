drop table if exists shares_folders;
drop table if exists shares_files;
drop table if exists files;
drop table if exists folders;
drop table if exists users;


create table users(
 id integer primary key,
 login text not null,
 password_checksum text not null
);

create table folders(
 id integer primary key,
 parent integer references folders(id),
 owner integer references users(id),
 name text not null
);

create table files (
 id integer primary key,
 owner integer not null references users(id),
 folder integer null references folders(id), -- корневая это null
 original_filename text, -- исходное имя файла, если известно
 server_filename text not null, -- путь к файлу на сервере (в БД только ссылка)
 url_filename text not null, -- уникальное имя файла для веба
 filesize integer not null,
 content_type text not null, -- тип файла для веба
 upload_date timestamp not null default current_date
);

create table shares_files(
 file integer references files(id),
 recipient integer references users(id),
 read_onle bool not null default true -- при false можно удалить, переименовать
);

create table shares_folders(
 folder integer references folders(id),
 recipient integer references users(id),
 read_onle bool not null default true -- при false можно удалить, переименовать
);


