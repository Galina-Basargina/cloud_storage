-- UTF-8 without BOM
-- скрипт выполняется с правами пользователя cs_user (см. 001.create_db.sql)
-- скрипт добавляет в схему таблицы аудита

drop view if exists coursework.audit_total;

drop trigger if exists shared_files_audit on coursework.shared_files;
drop trigger if exists files_audit on coursework.files;
drop trigger if exists shared_folders_audit on coursework.shared_folders;
drop trigger if exists folders_audit on coursework.folders;
drop trigger if exists auth_audit on coursework.auth;
drop trigger if exists users_audit on coursework.users;

drop function if exists coursework.process_shared_files_audit;
drop function if exists coursework.process_files_audit;
drop function if exists coursework.process_shared_folders_audit;
drop function if exists coursework.process_folders_audit;
drop function if exists coursework.process_auth_audit;
drop function if exists coursework.process_users_audit;

drop table if exists coursework.files_audit;
drop table if exists coursework.folders_audit;
drop table if exists coursework.users_audit;


create table coursework.users_audit (
 operation char(1) not null,
 created_at timestamp not null default current_timestamp,
 who integer not null,
 user_id integer not null,
 password_changed boolean
);

create table coursework.folders_audit (
 operation char(1) not null,
 created_at timestamp not null default current_timestamp,
 who integer not null,
 folder_id integer not null,
 parent integer,
 name text,
 recipient integer,
 read_only boolean
);

create table coursework.files_audit (
 operation char(1) not null,
 created_at timestamp not null default current_timestamp,
 who integer not null,
 file_id integer not null,
 folder integer,
 original_filename text,
 recipient integer,
 read_only boolean
);


--------------------------------------------------------------------------------
-- Users Audit
--------------------------------------------------------------------------------
create or replace function coursework.process_users_audit()
returns trigger as $$
declare auth_id integer;
begin
 if (tg_op = 'DELETE') then
  select coalesce(current_setting('cloud_storage.auth_id', true)::numeric, 0) into auth_id;
  insert into coursework.users_audit (operation, who, user_id)
  select 'D', auth_id, old.id;
  return old;
 elsif (tg_op = 'UPDATE') then
  select coalesce(current_setting('cloud_storage.auth_id', true)::numeric, 0) into auth_id;
  insert into coursework.users_audit (operation, who, user_id, password_changed)
  select 'U', auth_id, new.id, new.password_checksum <> old.password_checksum;
  return new;
 elsif (tg_op = 'INSERT') then
  insert into coursework.users_audit (operation, who, user_id)
  select 'I', new.id, new.id;
  return new;
 end if;
 return null;
end;
$$ language plpgsql;

create or replace trigger users_audit
 after insert or update or delete on coursework.users
 for each row execute procedure coursework.process_users_audit();

create or replace function coursework.process_auth_audit()
returns trigger as $$
declare auth_id integer;
begin
 if (tg_op = 'DELETE') then
  select coalesce(current_setting('cloud_storage.auth_id', true)::numeric, 0) into auth_id;
  insert into coursework.users_audit (operation, who, user_id)
  select 'E', auth_id, old.logged_in;
  return old;
 elsif (tg_op = 'INSERT') then
  insert into coursework.users_audit (operation, who, user_id)
  select 'A', new.logged_in, new.logged_in;
  return new;
 end if;
 return null;
end;
$$ language plpgsql;

create or replace trigger auth_audit
 after insert or delete on coursework.auth --or update
 for each row execute procedure coursework.process_auth_audit();

--------------------------------------------------------------------------------
-- Folders Audit
--------------------------------------------------------------------------------
create or replace function coursework.process_folders_audit()
returns trigger as $$
declare auth_id integer;
begin
 select coalesce(current_setting('cloud_storage.auth_id', true)::numeric, 0) into auth_id;
 if (tg_op = 'DELETE') then
  insert into coursework.folders_audit (operation, who, folder_id, parent, name)
  select 'D', auth_id, old.id, old.parent, old.name;
  return old;
 elsif (tg_op = 'UPDATE') then
  insert into coursework.folders_audit (operation, who, folder_id, parent, name)
  select 'U', auth_id, new.id, new.parent, new.name;
  return new;
 elsif (tg_op = 'INSERT') then
  insert into coursework.folders_audit (operation, who, folder_id, parent, name)
  select 'I', auth_id, new.id, new.parent, new.name;
  return new;
 end if;
 return null;
end;
$$ language plpgsql;

create or replace trigger folders_audit
 after insert or update or delete on coursework.folders
 for each row execute procedure coursework.process_folders_audit();

create or replace function coursework.process_shared_folders_audit()
returns trigger as $$
declare auth_id integer;
begin
 select coalesce(current_setting('cloud_storage.auth_id', true)::numeric, 0) into auth_id;
 if (tg_op = 'DELETE') then
  insert into coursework.folders_audit (operation, who, folder_id, recipient, read_only)
  select 'd', auth_id, old.folder, old.recipient, old.read_only;
  return old;
 elsif (tg_op = 'UPDATE') then
  insert into coursework.folders_audit (operation, who, folder_id, recipient, read_only)
  select 'u', auth_id, new.folder, new.recipient, new.read_only;
  return new;
 elsif (tg_op = 'INSERT') then
  insert into coursework.folders_audit (operation, who, folder_id, recipient, read_only)
  select 'i', auth_id, new.folder, new.recipient, new.read_only;
  return new;
 end if;
 return null;
end;
$$ language plpgsql;

create or replace trigger shared_folders_audit
 after insert or update or delete on coursework.shared_folders
 for each row execute procedure coursework.process_shared_folders_audit();

--------------------------------------------------------------------------------
-- Files Audit
--------------------------------------------------------------------------------
create or replace function coursework.process_files_audit()
returns trigger as $$
declare auth_id integer;
begin
 select coalesce(current_setting('cloud_storage.auth_id', true)::numeric, 0) into auth_id;
 if (tg_op = 'DELETE') then
  insert into coursework.files_audit (operation, who, file_id, folder, original_filename)
  select 'D', auth_id, old.id, old.folder, old.original_filename;
  return old;
 elsif (tg_op = 'UPDATE') then
  insert into coursework.files_audit (operation, who, file_id, folder, original_filename)
  select 'U', auth_id, new.id, new.folder, new.original_filename;
  return new;
 elsif (tg_op = 'INSERT') then
  insert into coursework.files_audit (operation, who, file_id, folder, original_filename)
  select 'I', auth_id, new.id, new.folder, new.original_filename;
  return new;
 end if;
 return null;
end;
$$ language plpgsql;

create or replace trigger files_audit
 after insert or update or delete on coursework.files
 for each row execute procedure coursework.process_files_audit();

create or replace function coursework.process_shared_files_audit()
returns trigger as $$
declare auth_id integer;
begin
 select coalesce(current_setting('cloud_storage.auth_id', true)::numeric, 0) into auth_id;
 if (tg_op = 'DELETE') then
  insert into coursework.files_audit (operation, who, file_id, recipient, read_only)
  select 'd', auth_id, old.file, old.recipient, old.read_only;
  return old;
 elsif (tg_op = 'UPDATE') then
  insert into coursework.files_audit (operation, who, file_id, recipient, read_only)
  select 'u', auth_id, new.file, new.recipient, new.read_only;
  return new;
 elsif (tg_op = 'INSERT') then
  insert into coursework.files_audit (operation, who, file_id, recipient, read_only)
  select 'i', auth_id, new.file, new.recipient, new.read_only;
  return new;
 end if;
 return null;
end;
$$ language plpgsql;

create or replace trigger shared_files_audit
 after insert or update or delete on coursework.shared_files
 for each row execute procedure coursework.process_shared_files_audit();

--------------------------------------------------------------------------------
-- Total Audit
--------------------------------------------------------------------------------
create or replace view coursework.audit_total as
 select
  case when operation = 'A' then 'login'
  when operation = 'E' then 'logoff'
  when operation = 'I' then 'register'
  when operation = 'U' then 'user edit'
  when operation = 'D' then 'user delete'
  else null end as operation,
  created_at as event_at,
  who,
  user_id as object_id
 from users_audit
   union
 select
  case when operation = 'I' then 'folder create'
  when operation = 'U' then 'folder edit'
  when operation = 'D' then 'folder remove'
  when operation = 'i' then 'share folder'
  when operation = 'u' then 'share folder setup'
  when operation = 'd' then 'unshare folder'
  else null end as operation,
  created_at,
  who,
  folder_id
 from folders_audit
   union
 select
  case when operation = 'I' then 'file upload'
  when operation = 'U' then 'file edit'
  when operation = 'D' then 'file remove'
  when operation = 'i' then 'share file'
  when operation = 'u' then 'share file setup'
  when operation = 'd' then 'unshare file'
  else null end as operation,
  created_at,
  who,
  file_id
 from files_audit;
