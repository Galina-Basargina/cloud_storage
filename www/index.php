<?php
if (!isset($_COOKIE['token'])) 
    $token = "";
else {
    $token = $_COOKIE['token'];
    if ($token == "null")
        $token = "";
}
    
if (empty($token)) { ?><!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход | Cloud Storage</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <div class="logo">
            <a href="index.html"><img src="logo-e0e0e0.png" alt="Cloud Logo"></a>
        </div>
        
        <h1>Вход в систему</h1>
        
        <form id="loginForm">
            <div class="form-group">
                <label>Имя пользователя</label>
                <input type="text" id="login" name="login" required>
            </div>

            <div class="form-group">
                <label>Пароль</label>
                <input type="password" id="password" name="password" required>
                <span class="password-toggle" onclick="togglePassword()">👁</span>
            </div>


            <div class="remember-me">
                <input type="checkbox" id="remember" name="remember">
                <label for="remember">Запомнить меня</label>
            </div>

            <button type="submit">Войти</button>
        </form>

        <!--<form id="tokenForm" method="post" action="index.php">
            <input type="text" name="token" hidden>
        </form>-->

        <div class="links">
            <a href="#">Забыли пароль?</a>
            <a href="register.html">Создать новый аккаунт</a>
        </div>
    </div>

    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
    <script src="storage.js"></script>
    <script>
        function togglePassword() {
            const passwordField = document.getElementById('password');
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);
        }

        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.stopPropagation();
            e.preventDefault();
            $.ajax({
                url: '/auth/login',
                method: 'post',
                //async:false,
                contentType: 'application/json',
                data: JSON.stringify({login: $(this).find('#login').val(), password: $(this).find('#password').val()}),
                success: function(data){storeToken(data.token);refreshPage();},
                error: function (jqXHR, exception) {
                    deleteCookie('token');
                    if (jqXHR.status === 0) alert('Not connect. Verify Network.');
                    else if (jqXHR.status == 401) alert('Ошибка входа: ' + jqXHR.responseText);
                    else if (jqXHR.status == 405) alert('Ошибка входа: ' + jqXHR.responseText);
                    else if (jqXHR.status == 404) alert('Requested page not found (404).');
                    else if (jqXHR.status == 500) alert('Internal Server Error (500).');
                    else if (exception === 'parsererror') alert('Requested JSON parse failed.'); // некорректный ввод post-params => return в .php, нет данных
                    else if (exception === 'timeout') alert('Time out error.'); // сервер завис?
                    else if (exception === 'abort') alert('Ajax request aborted.');
                    else alert('Uncaught Error. ' + jqXHR.responseText);
                }
            });
        });
    </script>
</body>
</html>
<?php } else { //phpinfo(); ?>
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Cloud Storage</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link rel="stylesheet" href="storage.css">
</head>
<body>
    <div class="container">
        <!-- Боковая панель -->
        <div class="sidebar">
            <h2>Папки</h2>
            <ul class="folder-tree" id="folderTree">
                <!-- Папки будут добавлены через JS -->
            </ul>
        </div>

        <!-- Основной контент -->
        <div class="main-content">
            <div class="header">
                <div>
                    <button class="button" onclick="createNewFolder()">
                        <i class="fas fa-folder-plus"></i> Новая папка
                    </button>
                    <button class="button" onclick="uploadFile()">
                        <i class="fas fa-upload"></i> Загрузить
                    </button>
                </div>
                <button class="button logout-btn" onclick="logout()">
                    <i class="fas fa-sign-out-alt"></i> Выход
                </button>
            </div>

            <div class="file-grid" id="fileGrid">
                <!-- Файлы будут добавлены через JS -->
            </div>
        </div>
    </div>

    <script src="storage.js"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
    <script>
        // Инициализация
        function init() {    
            modelGetData();
            viewChangeFolder();
        }

        // Функция выхода
        function logout() {
            if(!confirm('Вы действительно хотите выйти?')) return;
            deleteCookie('token');
            refreshPage();
        }

        // Дополнительные функции
        function createNewFolder() {
            const name = prompt('Введите название папки:');
            if (!name) return;
            modelCreateFolder(name);
        }

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

        // Инициализация при загрузке
        window.onload = init;
    </script>
</body>
</html><?php } ?>