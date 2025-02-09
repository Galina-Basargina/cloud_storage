<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход | Cloud Storage</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div class="container">
        <div class="logo">
            <a href="/"><img src="/logo-e0e0e0.png" alt="Cloud Logo"></a>
        </div>
        
        <h1>Вход в систему</h1>
        
        <form id="loginForm">
            <div class="form-group-login">
                <label>Имя пользователя</label>
                <input type="text" id="login" name="login" required>
            </div>

            <div class="form-group-login">
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

        <div class="links">
            <a href="#">Забыли пароль?</a>
            <a href="/register.php">Создать новый аккаунт</a>
        </div>
    </div>

    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
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
                async:false,
                contentType: 'application/json',
                data: JSON.stringify({login: $(this).find('#login').val(), password: $(this).find('#password').val()}),
                success: function(data){alert(data.token);},
                error: function (jqXHR, exception) {
                if (jqXHR.status === 0) alert('Not connect. Verify Network.');
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
