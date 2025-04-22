alter table coursework.shared_files alter column file set not null;
alter table coursework.shared_files drop constraint shared_files_unique;

create unique index shared_files_unique
    on coursework.shared_files using btree
    (file, recipient)
    where ((file is not null) and (recipient is not null));

create unique index shared_files_unique_public
    on coursework.shared_files using btree
    (file)
    where ((file is not null) and (recipient is null));
