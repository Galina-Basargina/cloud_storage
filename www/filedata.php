<?php
if (!isset($_COOKIE['token'])) 
    $token = "";
else {
    $token = $_COOKIE['token'];
    if ($token == "null")
        $token = "";
}

if (!isset($_GET['url'])) 
    $url = "";
else {
    $url = $_GET['url'];
    if ($url == "null")
        $url = "";
}

if (empty($token) || empty($url)) {
    include 'index.php';
    return;  // возврат на страницу логина или списка файлов
}

function getHttpCode($header): int {
    if(is_array($header)) {
        $parts=explode(' ',$header[0]);
        if(count($parts)>1) //HTTP/1.1 401 Unauthorized  => HTTP/?.? <code> <type>
            return intval($parts[1]);
    }
    return 0;
}

// получение полного url, например http://127.0.0.1:80/filedata/image.jpg
//$url = $_SERVER['REQUEST_SCHEME']."://".$_SERVER['REMOTE_ADDR'].":".$_SERVER['SERVER_PORT'].$url;
$url = "http://127.0.0.1:8080".$url;
// настройка авторизации для получения файла
$opts = array('http'=>array(
    'method'=>'GET',
    'header'=>"Authorization: Bearer $token\r\n"
));
// настройка запроса, который будет отправляться из этого скрипта
$context = stream_context_create($opts);
// отправка запроса
$file = file_get_contents($url, false, $context);
// успешно ли получены данные?
$http_code = getHttpCode($http_response_header); 
if ($http_code == 200) {
    // получение заголовков отввета
    $headers = implode("\n", $http_response_header);
    // получение content_type
    if (preg_match_all("/^content-type\s*:\s*(.*)$/mi", $headers, $matches)) {
        // если content_type удалось получить, то отправляем данные файла
        $content_type = end($matches[1]);
        header("Content-Type: $content_type");
        // вывод изображения
        echo $file;
        return;
    }
}
else if ($http_code == 401) {
    // ошибка авторизации
    include 'index.php';  // возврат на страницу логина или списка файлов
    return;
}
else {
    // все остальные ошибки
    http_response_code($http_code);
}
?>