2025-01-21 21:27
Теги: #

---
# Курсовая работа 3 курс

Тема курсовой работы - Создание облачного хранилища

Предварительно планируется доступ к хранилищу с помощью браузера, а также мобильного приложения.

Также выявлена проблемная часть в eduhouse (множество ссылок с яндекс и гугл диска не поддерживались). 

Одна из идея была синхронизация заметок Obsidian (его синхронизация платная, хотя идеология и устройство построено на бесплатном md формате)

## Проблематика работы с eduhouse

- https://disk.yandex.ru/client/disk?idApp=client&dialog=slider&idDialog=%2Fdisk%2F1629964185_texture_581784_3840x2400.jpg
- https://disk.yandex.ru/i/gY8IefXcL9sKdA
- https://1.downloader.disk.yandex.ru/preview/1e9d480e11b6afa438c4907c6c393ed4fde4e78b5c75e8ee328cc75bfb8ca834/inf/HOmH2_gAJVJV7wB3bewLEI_KuuWE_YoTtqu_7aZvAkWOS5zupBqb6EHDa2FGdxm0Vi5CbBhkK63ZYwmKCaRfpg%3D%3D?uid=878919296&filename=1629964185_texture_581784_3840x2400.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=878919296&tknv=v2&size=1920x1088
- https://docs.google.com/document/d/1ctQfhGwws8TdLm8Hnouht4DDLkBCn8lBrxH5HraIKHQ/edit?usp=drive_link

Во всех ссылка выше есть сложности с трансляцией названий. Выяснилось, что eduhouse пытается из ссылки сделать название, а потом создать файл в файловой системе по адресу /var/ww/tmp/... Иногда у него проблемы с неразрешенными символами. Эту проблему тоже предполагается решать.

Также ссылка на страницу с файлом на гугл диске - это ссылка на страницу, а не на сам файл и при работе с eduhouse пользователь это не ощущает и не понимает. Ссылка на файл не рабочая, так как нужны авторизационные куки, которые eduhouse передать не возможно. В итоге он файл загрузить не может.

Запрос на картинку из яндекс диска
```txt
GET /preview/1e9d480e11b6afa438c4907c6c393ed4fde4e78b5c75e8ee328cc75bfb8ca834/inf/HOmH2_gAJVJV7wB3bewLEI_KuuWE_YoTtqu_7aZvAkWOS5zupBqb6EHDa2FGdxm0Vi5CbBhkK63ZYwmKCaRfpg%3D%3D?uid=878919296&filename=1629964185_texture_581784_3840x2400.jpg&disposition=inline&hash=&limit=0&content_type=image%2Fjpeg&owner_uid=878919296&tknv=v2&size=1920x1088 HTTP/2
Host: 1.downloader.disk.yandex.ru
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3
Accept-Encoding: gzip, deflate, br, zstd
Referer: https://disk.yandex.ru/
Connection: keep-alive
Cookie: yuidss=6158364511681144296; _yasc=lc2qf...
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-site
If-Modified-Since: Tue, 21 Jan 2025 18:28:23 GMT
Priority: u=0, i
TE: trailers
```

Заголовок ответа сервера
```txt
HTTP/2 200 
content-length: 160121
date: Tue, 21 Jan 2025 18:28:41 GMT
timing-allow-origin: *
last-modified: Tue, 21 Jan 2025 18:28:41 GMT
content-disposition: inline; filename*=UTF-8''1629964185_texture_581784_3840x2400.jpg
nel: {"report_to": "neldrlog", "max_age": 604800, "success_fraction": 0.05, "failure_fraction": 0.5}
expires: Thu, 20 Feb 2025 18:28:41 GMT
x-content-type-options: nosniff
access-control-allow-origin: *
content-type: image/jpeg
report-to: {"group": "neldrlog", "max_age": 604800, "endpoints": [{"url": "https://dr.yandex.net/ya360/nel", "priority": 1}, {"url": "https://dr2.yandex.net/ya360/nel", "priority": 2}]}
x-request-id: 1737484120996325
cache-control: max-age=2592000
X-Firefox-Spdy: h2
```

Следует обратить внимание на параметр content-type, который определяет тип содержимого в данных ответа сервера. Данные могут быть картинкой, pdf...

# Проектирование БД

```sql
-- добавить сюда скрипт создания схемы базы данных после ее завершения
```

# Выбор способа клиент-серверного взаимодействия

![[Rest API]]



# Выбор подходящей платформы и языка программирования для серверной части

Поскольку работа предполагается крупная, время ограничено и надо успеть поработать над другими частями проекта, то основными критериями будут: скорость разработки, понятность кода и кроссплатформенность (хотя в первую очередь сервер будет работать под операционной системой linux).
Под эти три критерия подошли три языка программирования: Go, Rust, Python. 

При сравнении Python, Rust и Go для разработки облачного хранилища, каждый из языков имеет свои плюсы.

Python:
- Простота и читаемость кода, обеспечивающие быструю разработку.
- Огромное количество библиотек и фреймворков, что ускоряет создание REST API.

Rust:
- Высокая производительность и безопасность памяти, что делает его идеальным для системного программирования.
- Более сложная в изучении синтаксис, чем у Python.

Go:
- Отличная поддержка параллелизма, что важно для обработки больших объемов данных.
- Быстрая компиляция и хорошая производительность.

Хотя Rust и Go имеют свои преимущества, Python выигрывает благодаря простоте разработки и быстроте.


# Заметки о работе с базой данных (SQL-запросы)

## Работа с папками

```sql
insert into users (login, password_checksum) values ('galina', 'secret') returning id; -- POST

with deleted as (delete from users where id=16 returning *) select count(1) from deleted; -- DELETE

select login from users where id=19; -- GET with id

select id, login from users; -- GET without id
```

```sql
insert into folders(parent,owner,name) values(null,19,'') returning id; -- POST

with deleted as (delete from folders where id=1 returning *) select count(1) from deleted; -- DELETE

select parent,owner,name from folders where id=2; -- GET with id
  
select id,parent,owner,name from folders; -- GET without id

update folders set parent=12, name='folder5' where id=14 and owner=19 returning id; -- PUT
```

После того как было принято решение автоматически создавать корневую папку для каждого пользователя, запрос создания пользователя изменился (первая версия не заработала):
```sql
-- Первая версия:
--begin transaction;
--do $$
--declare
--u int;
--begin
--with inserted as (insert into users(login,password_checksum) values('admin2','123') returning id)
--select id into u from inserted;
--insert into folders(parent,owner,name) values(null,u,'');
--return u;
--end$$;
--commit;

-- Вторая версия (рабочая)
begin transaction;
 insert into users(login,password_checksum)
 values('admin1','123')
 returning id; -- fetch one
 insert into folders(parent,owner,name) values(null,:id,'');
commit;
```

Кроме того, корневая папка у пользователя имеет пустое название, но признаком корневой папки является `parent=null`. Также пользователю запрещено создавать не корневые папки.

Кроем того, для проверки владельца корневой папки, запрос запрос с простым insert-ом пришлось модернизировать:
```sql
-- Было:
--insert into folders(parent,owner,name)
--values(null,19,'')
--returning id; -- POST

-- Стало v1:
insert into folders(parent,owner,name)
select 8,19,'folder'
where 19 in (select owner from folders where id=8)
returning id; -- POST

-- Стало v2:
insert into folders(parent,owner,name)
select 8,19,'folder'
where
 19 in (select owner from folders where id=8) and
 (select id from folders where parent=8 and name='folder') is null
returning id; -- POST
```

Первая версия не дает создавать свои папки в чужих папках, а вторая версия дополнительно запрещает создавать папки с одинаковыми названиями в одном месте.

Также, при создании схемы базы данных пришлось добавить ограничение на таблицу folders: `ADD CONSTRAINT folders_unique UNIQUE (parent, name)` для того, чтобы никакая другая программа не могла создать ошибочную папку.

Для удаления вложенных папок потребовалось получать идентификаторы папок на всех уровнях вложенности. Для этого воспользовалась рекурсивным запросом. Ниже приведен запрос получения идентификаторов, и запрос удаления вложенных папок:

```sql
-- запрос позволяет получить все идентификаторы вложенных папок
with recursive r(id) as (
 select id,parent from folders
 where id=2
union
 select f.id,f.parent from folders f
 join r on (f.parent=r.id)
)
select id from r;

-- удаляет папки и возвращает количество удалённых
-- количество удалённых папок - необязательное дополнение к запросу
-- для удаления достаточно только delete from... без returning
with deleted as (
 delete from folders where id in (
  with recursive r(id) as (
   select id,parent from folders
   where id=2 and parent is not null -- кроме корнеквой папки
  union
   select f.id,f.parent from folders f
   join r on (f.parent=r.id)
  )
  select id from r
 ) returning *
)
select count(1) from deleted;
```

Примечание: рекурсивный запрос работает итеративно, то есть поднимается с одного уровня вложенности, на следующий - эта механика не является частью SQL, которая работает с множествами. Именно поэтому рекурсивные запросы не часть SQL, а дополнение, которое индивидуально у PostgreSQL. В других серверах этот синтаксис работать не будет.

В ходе работы потребовалось взаимодействовать со сложными структурированными данными, отлаживать работу удаления. Для удобства воспользовалась простой схемой создания backup-таблицы:

```sql
create table T as select * from folders;
delete from folders;
insert into folders select * from t;
```

## Работа с файлами

Так как работа с папками и файлами очень похожа, то все запросы были сделаны по подобию работы с папками.

```sql
-- создание файла 
insert into files ("owner", folder, original_filename, server_filename, url_filename, filesize, content_type) 
values (31, 18, 'filename', 'server_name', 'cat.png', 256, 'png') returning id;


insert into files ("owner", folder, original_filename, server_filename, url_filename, filesize, content_type)
select 
 31,
 18,
 'cat.png',
 '/var/lib/cloud_storage/c086a9ef307700de',
 '/filedata/76d93ea7.png',
 256,
 'image/png'
where
 31 in (select owner from folders where id=18) and
 (select id from files where folder=18 and original_filename='cat.png') is null
returning id;


-- выборка всех файлов пользователя
select id, "owner", folder, original_filename, url_filename, filesize, content_type, upload_date
from files  
where "owner" = 31;

-- выборка данных о файле по указанному id
select "owner", folder, original_filename, url_filename, filesize, content_type, upload_date  
from files  
where id=2 and owner=31;

-- изменение данных о файле, v1
update files set (список изменений) 
 where id=2 and owner=31 
returning id;

-- удаление файла
with deleted as (
 delete from files 
  where id=2 and "owner"=31 
 returning *)
```

При реализации работы с файлами было замечено, что еще не сделана проверка на наличие файла (папки) с таким же названием в одном и местоположении.

В процессе работы над моделью данных потребовалось загружать данные из корневой папки, но без идентификатора это сделать невозможно. Потребовались данные о корневой папке пользователя, поэтому пришлось поменять запрос о получении информации о пользователе:

```sql
-- раньше
select login from users where id=31;

-- стало
select
 login,
 f.id as root_folder
from
 users u
  join folders f on (f.owner = u.id and f.parent is null)
where u.id=31;
```

## Веб-доступ к облачному хранилищу

Несмотря на то, что был изготовлен http сервер для работы с файлами и папками, все же это внутренний функционал системы, построенный на базе rest-запросов. Для того, чтобы сделать активную часть сайта (обложка, регистрация пользователя, список папок и файлов), изобретать велосипед не буду, воспользуюсь языком программирования php. При этом веб-сервер буду использовать nginx. А запросы с веб-сервера на мой http-сервер буду проксировать (на эту тему у нас были лабораторные работы в конце января 2025 года)

To Do:
- Добавить блок схему серверов и браузера
```txt
title Cloud Storage

Браузер->Nginx: GET /
activate Браузер
activate Nginx

Nginx->Браузер: index.html
deactivate Nginx

Браузер->Nginx: GET style.css
activate Nginx
Nginx->Браузер: style.css
deactivate Nginx

Браузер->Nginx: GET script.js
activate Nginx
Nginx->Браузер: script.js
deactivate Nginx
```

![[browser2nginx.png]]

```txt
title Cloud Storage

actor User

User->Браузер: Login

activate Браузер
Браузер->Nginx: GET /login.html
activate Nginx
Nginx->Браузер: login.html
deactivate Nginx
Браузер->Nginx: GET /style.css
activate Nginx
Nginx->Браузер: style.css
deactivate Nginx
deactivate Браузер

User->Браузер: Отправка логина и пароля

activate Браузер
Браузер->Браузер: JS метод (ajax)
activate Браузер
deactivate Браузер
Браузер->Nginx: POST /auth/login
activate Nginx
Браузер-->CloudServer: POST /auth/login (proxy)
activate CloudServer
CloudServer->DB: select users
activate DB
DB->CloudServer: return user
CloudServer->DB: insert auth
DB->CloudServer: return OK
deactivate DB
CloudServer-->Браузер: token (proxy)
deactivate CloudServer
Nginx->Браузер: token
deactivate Nginx
Браузер->Браузер: запомнить token
activate Браузер
deactivate Браузер
deactivate Браузер
```

![[browser2proxy2server.png]]

По сути браузер будет получать html-страничку от nginx-сервера, а также CSS и JavaScript код с того же сервера. 

JavaScript во время своей работы будет отправлять запросы на nginx, а он будет их проксировать в моё облачное хранилище. Результат будет возвращаться через nginx в браузер, а браузер с помощью JS будет анализировать результаты. 

На картинке ниже рассмотрен вариант авторизации пользователя.

![[dfd_web-site.png]]

Полное взаимодействие гораздо сложнее, например страница регистрации тоже отправляет запрос на Cloud Server, что на диаграмме не показано.

## Настройка VPS в интернете

![[Настройка Arch Linux]]

### Настройка nginx (Debian), php

```bash
sudo apt install nginx
sudo apt install php8.1-fpm  # версия зависит от nginx и ОС

sudo cat > /etc/nginx/sites-available/cloud-storage <<EOF
server {
	listen 80 default_server;
	listen [::]:80 default_server;
	root /var/www/cloud_storage;
	index index.html index.htm index.php;
	server_name _;
	location / {
		try_files $uri $uri/ =404;
	}
	location ~ ^/(auth/login|auth/logout|users|folders|files|filedata/) {
		proxy_pass http://127.0.0.1:8080;
	}
	location ~ \.php$ {
		include snippets/fastcgi-php.conf;
		fastcgi_pass unix:/run/php/php8.1-fpm.sock;
	}
	location ~ /\.ht {
		deny all;
	}
}
EOF

sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/cloud-storage \
           /etc/nginx/sites-enabled/cloud-storage

sudo systemctl restart nginx
```

### Настройка nginx (Arch), php и Cloud Storage

```bash
sudo pacman -S nginx
pacman -Ss php | grep fpm # поиск пакета php?.?-fpm
sudo pacman -S php-fpm
sudo pacman -S git

sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl enable php-fpm
sudo systemctl start php-fpm

sudo ufw allow 80/tcp comment "www"

# на ноутбуке: проверить, что открывается сайт http://336707.simplecloud.ru

# в файле /etc/nginx/nginx.conf найти и закомментировать server { }
# в конец секции http добавить строку include /etc/nginx/sites-enabled/*;

sudo mkdir -p /opt/cloud_storage
cd /opt/cloud_storage
sudo git clone https://github.com/Galina-Basargina/cloud_storage.git .

sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled
sudo tee <<EOF /etc/nginx/sites-available/cloud-storage >/dev/null
server {
	listen 80 default_server;
	listen [::]:80 default_server;
	root /opt/cloud_storage/www;
	index index.html index.htm index.php;
	server_name 336707.simplecloud.ru;
	location / {
		try_files \$uri \$uri/ =404;
	}
	location ~ ^/(auth/login|auth/logout|users|folders|files|filedata/) {
		proxy_pass http://127.0.0.1:8080;
	}
	location ~ \.php\$ {
		#include snippets/fastcgi-php.conf;
		fastcgi_split_path_info ^(.+?\.php)(/.*)\$;
		try_files \$fastcgi_script_name =404;
		set \$path_info \$fastcgi_path_info;
		fastcgi_param PATH_INFO \$path_info;
		fastcgi_index index.php;
		include fastcgi.conf;
		fastcgi_pass unix:/run/php-fpm/php-fpm.sock;
	}
	location ~ /\.ht {
		deny all;
	}
	client_max_body_size 20M;
}
EOF

sudo ln -s /etc/nginx/sites-available/cloud-storage \
           /etc/nginx/sites-enabled/cloud-storage
```

Настройка REST CloudServer:

```bash
sudo pacman -S python3
sudo pacman -S postgresql
sudo pacman -S python-psycopg2
sudo pacman -S screen

# создание базы данных от имени postgres с правами postgres
sudo -S -u postgres initdb -D /var/lib/postgres/data

# запуск сервера баз данных
sudo systemctl enable postgresql
sudo systemctl start postgresql
sudo systemctl status postgresql

# создание базы данных и пользователя
sudo -S -u postgres psql postgres postgres
# команды из /opt/cloud_storage/database/001.create_db.sql
# CREATE DATABASE cs_db WITH ENCODING = 'UTF8' CONNECTION LIMIT = -1;
# CREATE USER cs_user WITH LOGIN PASSWORD 'cs_m5SJaMkbZ7d9' NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
# GRANT ALL ON DATABASE cs_db TO cs_user;

# создание схемы базы данных
cd /opt/cloud_storage/database
sudo -S -u postgres psql --file=002.create_schema.sql cs_db cs_user

# настройка python, установка зависимостей
cd /opt/cloud_storage/server
sudo python3 -m venv .venv
sudo .venv/bin/python -m pip install -r requirements.txt

# выдаем права на сохранение загруженных файлов
sudo chmod 775 /opt/cloud_storage/files
sudo chown root:$USER /opt/cloud_storage/files

# проверка, что сервер запускается
cd /opt/cloud_storage/server
.venv/bin/python server.py \
	--address=127.0.0.1 --port=8080 \
	--dbname=cs_db --dbuser=cs_user \
	--dbpassword=cs_m5SJaMkbZ7d9 --dbschema=coursework \
	--storage=/opt/cloud_storage/files
# Database connected: ('PostgreSQL 17.2 on x86_64-pc-linux-gnu, 
# compiled by gcc (GCC) 14.2.1 20250128, 64-bit',)
# Running server at 127.0.0.1:8080
# ^C
# Server stopped
# Database disconnected

screen
# cd /opt/cloud_storage/server
# команда запуска сервера
```


/var/www/cloud_storage$ sudo ln /home/galina/Workspace/cloud_storage/www/logo-e0e0e0.png logo-e0e0e0.png

## Получение содержимого файла

Потребовалось сделать свой собственный proxy, который берёт token из cookie и url из параметров, после чего отправляет запрос на свой собственный сервер, получает результат, выделяет из него данные и content_type, отправляя его обратно в качестве ответа.

```php
// получение полного url, например http://127.0.0.1:80/filedata/image.jpg
$url = $_SERVER['REQUEST_SCHEME']."://".$_SERVER['REMOTE_ADDR'].":".$_SERVER['SERVER_PORT'].$url;
// настройка авторизации для получения файла
$opts = array('http'=>array(
  'method'=>'GET',
  'header'=>"Authorization: Bearer $token\r\n"
));
// настройка запроса, который будет отправляться из этого скрипта
$context = stream_context_create($opts);
// отправка запроса
$file = file_get_contents($url, false, $context);
// получение заголовков отввета
$headers = implode("\n", $http_response_header);
// получение content_type
if (preg_match_all("/^content-type\s*:\s*(.*)$/mi", $headers, $matches)) {
  // если content_type удалось получить, то отправляем данные файла
  $content_type = end($matches[1]);
  header("Content-Type: $content_type");
  // вывод изображения
  echo $file;
}
```

Пример выше укорочен, в нем нет обработки ошибок, полный пример смотри в приложении с исходными кодами.
https://stackoverflow.com/questions/25237100/how-to-get-mime-type-of-an-image-with-file-get-contents-in-php

## Загрузка файлов

Загрузка делится на две части: действия в браузере и действия на сервере. В браузере выбирается файл, получаются его параметры и содержимое, отправляется на сервер. На сервере файл принимается (все данные передаются в json-формате, поэтому файл передается как base64).

```js
function uploadFile() {
  // создание элемента input для выбора файла (одного)
  var input = document.createElement('input');
  input.type = 'file';
  input.multiple = false;
  input.onchange = e => {
    // событие выбора файла
    var file = e.target.files[0];
    // начинаем читать данные файла
    var reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = readerEvent => {
    // событие успешного прочтения данных файла
    var content = readerEvent.target.result;
    modelUploadFile(file.name, file.size, file.type, content);
    }
}
input.click();
}
```

https://stackoverflow.com/a/40971885

```python
base64_data = request['base64']  
if ';base64,' in base64_data:  
	__header, base64_data = base64_data.split(';base64,')  
try:  
	decoded_file = base64.b64decode(base64_data)  
except (TypeError, binascii.Error, ValueError):  
	response = {'error': 'unsupported request, invalid file data'}
#...
with open(f"{storage}/{server_filename}", "wb+") as f:  
	f.write(decoded_file)  
	f.close()
```

для снятия ограничения на длину загрузки файлов необходимо в настройки nginx.conf добавить:

```txt
client_max_body_size 20M;
```

## Java Android

Изначально для добавления в проект сетевого взаимодействия потребовалось сделать первые шаги отсюда: https://stackoverflow.com/a/39385674

Простейший пример с использованием retrofit: https://github.com/square/retrofit/blob/trunk/samples/src/main/java/com/example/retrofit/SimpleService.java

Использование retrofit привело к сбою android.os.NetworkOnMainThreadException при отправке запроса из основного Activity - так нельзя. Решение вот: https://stackoverflow.com/a/35482308

Пример работы с Rest-запросами: https://habr.com/ru/articles/428736/

Пример отправки POST-запроса: https://www.csharp.com/article/call-post-api-in-android-using-retrofit/

Настройка использования http без шифрования: https://stackoverflow.com/a/53349252

Поскольку удобного способа отслеживания/отладки обмена сообщениями (как в браузере) в android клиенте нет, то пришлось просматривать сообщения на сервере:

```bash
sudo pacman -S tcpdump
sudo tcpdump -vvv 'tcp port 80'
```

### Java Android SQLite

В ходе работы над сохранением настроек в android-приложении потребовалось создать "вечноживущий" экземпляр объекта с параметрами. Воспользовалась шаблоном проектирования Singleton (Одиночка): https://en.wikipedia.org/wiki/Singleton_pattern#Lazy_initialization

###  Java ModelView

ссылка по работе с MutableLiveData: https://medium.com/@taman.neupane/basic-example-of-livedata-and-viewmodel-14d5af922d0

ссылка, объясняющая работу ViewModel: https://metanit.com/java/android/10.2.php - добавить в отчет то, что ModelView хранит те данные, которые могут случайно уничтожиться при перевороте экрана.

## Аудит. Журнализация действий пользователя

В целях обучения работы с триггерами в PostgreSQL была выбрана задача автоматической журнализации действий пользователей. Аудит будем делать с помощью триггеров (логики расположенной на сервере, то есть хранимые процедуры расположенные на сервере).

Действия, аудит которых будет выполняться:
- Действия с пользователем:
	- (A) Аутентификация пользователя (insert в auth)
	- (E) Выход/отключение пользователя (delete из auth) 
	- (I) Добавление пользователя (insert в users)
	- (U) Редактирование данных пользователя, например пароль (update users)
	- (D) Удаление пользователя (delete из users)
- Действия с папками:
	- (I) Создание папки (insert в folders)
	- (D) Удаление папки (delete из folders)
	- (U) Перемещение или переименование папки (update folders)
	- (i) Предоставление доступа к папке (insert в shared_folders)
	- (d) Удаление доступа к папке (delete из shared_folders)
	- (u) Изменение настроек доступа к папке (update shared_folders)
- Действия с файлами:
	- (I) Загрузка файла (insert в files)
	- (D) Удаление файла (delete из files)
	- (U) Перемещение или переименование файла (update files)
	- (i) Предоставление доступа к файлу (insert в shared_files)
	- (d) Удаление доступа к файлу (delete из shared_files)
	- (u) Изменение настроек доступа к файлу (update shared_files)

В списках выше проставлены коды операций (буквы), которые будут сохраняться в таблицах аудита.  

# План:
1. Развить базу так, чтобы она отдельно была как проект (создать функции по заполнению данных), сделать код по тригеру и тп....
2. сделать устаревание токенов по времени
3. -----
4. дописать раздел из ChatGPT про "пример того, как делается авторизация в rest"
5. переделать автоматическое появление папки в триггер
6. создать несколько view
7. ~~сделать валидность паролей~~
8. сделать отправление на почту логина и пароля
9. 

---
### Zero-ссылки
- [[00 Курсовая]]
---
### Ссылки
- https://skillbox.ru/media/code/chto_takoe_api/?utm_source=media&utm_medium=link&utm_campaign=all_all_media_links_links_articles_all_all_skillbox - Что такое API и как он работает
- https://skillbox.ru/media/code/rest-api-chto-eto-takoe-i-kak-rabotaet/ - REST API: что это такое и как работает
- https://restfulapi.net/http-methods/
- https://stackoverflow.com/questions/6083132/postgresql-insert-into-select
- https://habr.com/ru/companies/ruvds/articles/559816/
- https://habr.com/ru/companies/yandex_praktikum/articles/754682/
- https://sky.pro/wiki/python/sozdanie-rest-api-klienta-na-python/
- https://habr.com/ru/articles/268617/
- https://skillbox.ru/media/code/rust-zachem-on-nuzhen-gde-primenyaetsya-i-za-chto-ego-vse-lyubyat/
- https://gb.ru/blog/relyatsionnaya-baza-dannykh/
- https://www.w3schools.com/js/js_cookies.asp - работа с куки на js