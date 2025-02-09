<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Регистрация | Cloud Storage</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div class="container">
        <div class="logo">
            <a href="/"><img src="/logo-e0e0e0.png" alt="Cloud Logo"></a>
        </div>
        
        <h1>Создать аккаунт</h1>
        
        <form id="registrationForm">
            <div class="form-group-register">
                <label>Имя пользователя</label>
                <input type="text" required>
            </div>

            <div class="form-group-register">
                <label>Электронная почта</label>
                <input type="email" required>
            </div>

            <div class="form-group-register">
                <label>Пароль</label>
                <input type="password" required minlength="8">
                <div class="password-rules">Минимум 8 символов, включая цифры и спецсимволы</div>
            </div>

            <div class="terms">
                <input type="checkbox" id="terms" required>
                <label for="terms">Я принимаю условия использования и политику конфиденциальности</label>
            </div>

            <button type="submit">Зарегистрироваться</button>
        </form>

        <div class="login-link">
            Уже есть аккаунт? <a href="/login.php">Войти</a>
        </div>
    </div>

    <script>
        document.getElementById('registrationForm').addEventListener('submit', function(e) {
            e.preventDefault();
            // Здесь можно добавить логику обработки формы
            alert('Форма успешно отправлена!');
        });
    </script>
</body>
</html>

