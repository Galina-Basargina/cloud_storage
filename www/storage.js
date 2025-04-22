var today = new Date();
var expiry = new Date(today.getTime() + 24*3600*1000);
var setCookie = function(name, value) {
    document.cookie=name + "=" + escape(value) + "; path=/; expires=" + expiry.toGMTString();
};
var deleteCookie = function(name) {
    document.cookie=name + "=null; path=/; expires=" + expiry.toGMTString();
};
function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for(let i = 0; i <ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ')
            c = c.substring(1);
        if (c.indexOf(name) == 0) {
            let val=c.substring(name.length, c.length);
            if (val === "null") return "";
            return val;
        }
    }
    return "";
}

function storeToken(token) {
    setCookie('token', token);
}

function refreshPage() {
    // POST
    //var frm = $("#tokenForm");
    //frm.find("input[name='token']").val('token');
    //frm.submit();
    // GET
    window.location = window.location.href;
}

function logoutOnAuthError(){
    deleteCookie('token');
    refreshPage();
}

// Logoff пользователя
function logoutByRequest(){
    let token = getCookie('token');
    if (!token) return;
    $.ajax({
        url: '/auth/logout',
        method: 'get',
        async:false, // ждем ответ
        // contentType: 'application/json',
        // data: JSON.stringify({}),
        headers: {'Authorization': 'Bearer '+token},
        // success: function(data){},
        error: function (jqXHR, exception) {
            if (jqXHR.status === 0) alert('Not connect. Verify Network.');
            else if (jqXHR.status == 400) alert('Bad request (400).');
            else if (jqXHR.status == 500) alert('Internal Server Error (500).');
            else if (exception === 'parsererror') alert('Requested JSON parse failed.'); // некорректный ввод post-params => return в .php, нет данных
            else if (exception === 'timeout') alert('Time out error.'); // сервер завис?
            else if (exception === 'abort') alert('Ajax request aborted.');
            else alert('Uncaught Error. ' + jqXHR.responseText);
        }
    });
}

//---------- ----------
// поддержка модели данных (MODEL)
//---------- ----------

var modelData = {
    root_folder: null,
    current_folder: {id: null, parent: null, name: null},
    folders: [
        // {id: 18, parent: 8, name: 'folder1'},
    ],
    files: [
        // {id: 5, original_filename: 'car.jpg', url_filename: '/???',
        //  filesize: 100, content_type: 'image/jpg', upload_date: '2025-02-03',
        //  share: {public: false, private: [40,16]}
        // }
    ]
};

// вызывается при сбое загрузки текущей папки (папку кто-то удалил)
function modelErrorOnLoadFolder(){
    modelGetFoldersAndFiles(modelData.root_folder);
}

// сохраняет полученные c сервера данные в модель
function modelStoreCurrentFolder(folder_id, data){
    modelData.current_folder.id = folder_id;
    modelData.current_folder.parent = data.parent;
    modelData.current_folder.name = data.name;
}

// сохраняет папки в модель по указанной папке
function modelStoreFolders(folder_id, data){
    data.folders.forEach((folder) => { 
        if (folder.parent == folder_id){
            modelData.folders.push({
                id: folder.id,
                parent: folder_id,
                name: folder.name
            });
        }
    })
}

// сохраняет файлы в модель по указанной папке
function modelStoreFiles(folder_id, data){
    data.files.forEach((file) => { 
        if (file.folder == folder_id){
            modelData.files.push({
                id: file.id,
                // folder: folder_id,
                original_filename: file.original_filename,
                url_filename: file.url_filename,
                filesize: file.filesize,
                content_type: file.content_type,
                upload_date: file.upload_date,
                share: {public: file.public, private: []}
            });
        }
    })
}

// Поиск данных файла по id
function modelFindFileById(file_id) {
    var res = null;
    modelData.files.forEach((file) => { 
        if (file.id == file_id){
            res = file;
        }
    })
    return res;
}

// загружает данные модели по указанной папке
// если произойдет ошибка авторизации, страница перезагружается
function modelGetFoldersAndFiles(folder_id){
    modelData.current_folder.parent = null;
    modelData.current_folder.name = null;
    modelData.folders = [];
    modelData.files = [];
    // получаем данные о текущей папке
    $.ajax({
        url: '/folders/'+folder_id,
        method: 'get',
        async:false, // ждем ответ
        contentType: 'application/json',
        // data: JSON.stringify({}),
        headers: {'Authorization': 'Bearer '+getCookie('token')},
        success: function(data){modelStoreCurrentFolder(folder_id,data);},
        error: function (jqXHR, exception) {
            if (jqXHR.status === 0) alert('Not connect. Verify Network.');
            else if (jqXHR.status == 401) logoutOnAuthError();
            else if (jqXHR.status == 404) modelErrorOnLoadFolder();
            else if (jqXHR.status == 400) alert('Bad request (400).');
            else if (jqXHR.status == 500) alert('Internal Server Error (500).');
            else if (exception === 'parsererror') alert('Requested JSON parse failed.'); // некорректный ввод post-params => return в .php, нет данных
            else if (exception === 'timeout') alert('Time out error.'); // сервер завис?
            else if (exception === 'abort') alert('Ajax request aborted.');
            else alert('Uncaught Error. ' + jqXHR.responseText);
        }
    });
    // получаем данные о папках
    $.ajax({
        url: '/folders',
        method: 'get',
        async:false, // ждем ответ
        contentType: 'application/json',
        // data: JSON.stringify({}),
        headers: {'Authorization': 'Bearer '+getCookie('token')},
        success: function(data){modelStoreFolders(folder_id, data);},
        error: function (jqXHR, exception) {
            if (jqXHR.status === 0) alert('Not connect. Verify Network.');
            else if (jqXHR.status == 401) logoutOnAuthError();
            else if (jqXHR.status == 404) modelErrorOnLoadFolder();
            else if (jqXHR.status == 400) alert('Bad request (400).');
            else if (jqXHR.status == 500) alert('Internal Server Error (500).');
            else if (exception === 'parsererror') alert('Requested JSON parse failed.'); // некорректный ввод post-params => return в .php, нет данных
            else if (exception === 'timeout') alert('Time out error.'); // сервер завис?
            else if (exception === 'abort') alert('Ajax request aborted.');
            else alert('Uncaught Error. ' + jqXHR.responseText);
        }
    });
    // получаем данные о файлах
    $.ajax({
        url: '/files',
        method: 'get',
        async:false, // ждем ответ
        contentType: 'application/json',
        // data: JSON.stringify({}),
        headers: {'Authorization': 'Bearer '+getCookie('token')},
        success: function(data){modelStoreFiles(folder_id, data);},
        error: function (jqXHR, exception) {
            if (jqXHR.status === 0) alert('Not connect. Verify Network.');
            else if (jqXHR.status == 401) logoutOnAuthError();
            else if (jqXHR.status == 404) modelErrorOnLoadFolder();
            else if (jqXHR.status == 400) alert('Bad request (400).');
            else if (jqXHR.status == 500) alert('Internal Server Error (500).');
            else if (exception === 'parsererror') alert('Requested JSON parse failed.'); // некорректный ввод post-params => return в .php, нет данных
            else if (exception === 'timeout') alert('Time out error.'); // сервер завис?
            else if (exception === 'abort') alert('Ajax request aborted.');
            else alert('Uncaught Error. ' + jqXHR.responseText);
        }
    });
}

// полностью загружает данные модели
function modelGetData(){
    if (modelData.root_folder === null){
        // получаем данные о пользователе
        modelGetUserData();
    }
    modelGetFoldersAndFiles(modelData.root_folder);
}

// заполнение данных о пользователе в модели данных
// если произойдет ошибка авторизации, страница перезагружается
function modelGetUserData(){
    $.ajax({
        url: '/users/me',
        method: 'get',
        async:false, // ждем ответ
        contentType: 'application/json',
        // data: JSON.stringify({}),
        headers: {'Authorization': 'Bearer '+getCookie('token')},
        success: function(data){modelData.root_folder=data.root_folder;},
        error: function (jqXHR, exception) {
            if (jqXHR.status === 0) alert('Not connect. Verify Network.');
            else if (jqXHR.status == 401) logoutOnAuthError();
            else if (jqXHR.status == 404) logoutOnAuthError();
            else if (jqXHR.status == 400) alert('Bad request (400).');
            else if (jqXHR.status == 500) alert('Internal Server Error (500).');
            else if (exception === 'parsererror') alert('Requested JSON parse failed.'); // некорректный ввод post-params => return в .php, нет данных
            else if (exception === 'timeout') alert('Time out error.'); // сервер завис?
            else if (exception === 'abort') alert('Ajax request aborted.');
            else alert('Uncaught Error. ' + jqXHR.responseText);
        }
    });
}

// создание новой папки и перезагрузка модели
function modelCreateFolder(name){
    $.ajax({
        url: '/folders',
        method: 'post',
        //async: false,
        contentType: 'application/json',
        headers: {'Authorization': 'Bearer '+getCookie('token')},
        data: JSON.stringify({name: name, parent: modelData.current_folder.id}),
        success: function(data){
            modelGetFoldersAndFiles(modelData.current_folder.id);
            viewChangeFolder();
        },
        error: function (jqXHR, exception) {
            if (jqXHR.status === 0) alert('Not connect. Verify Network.');
            else if (jqXHR.status == 401) logoutOnAuthError();
            else if (jqXHR.status == 404) alert('Requested page not found (404).');
            else if (jqXHR.status == 400) alert('Bad request (400).');
            else if (jqXHR.status == 500) alert('Internal Server Error (500).');
            else if (exception === 'parsererror') alert('Requested JSON parse failed.'); // некорректный ввод post-params => return в .php, нет данных
            else if (exception === 'timeout') alert('Time out error.'); // сервер завис?
            else if (exception === 'abort') alert('Ajax request aborted.');
            else alert('Uncaught Error. ' + jqXHR.responseText);
        }
    });
}

// загрузка нового файла и перезагрузка модели
function modelUploadFile(name, size, content_type, content){
    $.ajax({
        url: '/files',
        method: 'post',
        //async: false,
        contentType: 'application/json',
        headers: {'Authorization': 'Bearer '+getCookie('token')},
        data: JSON.stringify({
            original_filename: name,
            folder: modelData.current_folder.id,
            content_type: content_type,
            size: size,
            base64: content
        }),
        success: function(data){
            modelGetFoldersAndFiles(modelData.current_folder.id);
            viewChangeFolder();
        },
        error: function (jqXHR, exception) {
            if (jqXHR.status === 0) alert('Not connect. Verify Network.');
            else if (jqXHR.status == 401) logoutOnAuthError();
            else if (jqXHR.status == 404) alert('Requested page not found (404).');
            else if (jqXHR.status == 400) alert('Bad request (400).');
            else if (jqXHR.status == 500) alert('Internal Server Error (500).');
            else if (exception === 'parsererror') alert('Requested JSON parse failed.'); // некорректный ввод post-params => return в .php, нет данных
            else if (exception === 'timeout') alert('Time out error.'); // сервер завис?
            else if (exception === 'abort') alert('Ajax request aborted.');
            else alert('Uncaught Error. ' + jqXHR.responseText);
        }
    });
}

// расшаривание файла без перезагрузки модели
function modelShareFileToPublic(file_id) {
    $.ajax({
        url: '/share',
        method: 'post',
        async: false,
        contentType: 'application/json',
        headers: {'Authorization': 'Bearer '+getCookie('token')},
        data: JSON.stringify({type: 'public', file_id: file_id}),
        success: function(data){
            modelGetFoldersAndFiles(modelData.current_folder.id);
            viewChangeFolder();
        },
        error: function (jqXHR, exception) {
            if (jqXHR.status === 0) alert('Not connect. Verify Network.');
            else if (jqXHR.status == 401) logoutOnAuthError();
            else if (jqXHR.status == 404) alert('Requested file not found (404).');
            else if (jqXHR.status == 400) alert('Bad request (400).');
            else if (jqXHR.status == 500) alert('Internal Server Error (500).');
            else if (exception === 'parsererror') alert('Requested JSON parse failed.'); // некорректный ввод post-params => return в .php, нет данных
            else if (exception === 'timeout') alert('Time out error.'); // сервер завис?
            else if (exception === 'abort') alert('Ajax request aborted.');
            else alert('Uncaught Error. ' + jqXHR.responseText);
        }
    });
}

// переименование файла и перезагрузка модели
function modelRenameFile(file_id, file_name) {
    $.ajax({
        url: '/files/'+file_id,
        method: 'patch',
        async: false,
        contentType: 'application/json',
        headers: {'Authorization': 'Bearer '+getCookie('token')},
        data: JSON.stringify({original_filename: file_name}),
        success: function(data){
            modelGetFoldersAndFiles(modelData.current_folder.id);
            viewChangeFolder();
        },
        error: function (jqXHR, exception) {
            if (jqXHR.status === 0) alert('Not connect. Verify Network.');
            else if (jqXHR.status == 401) logoutOnAuthError();
            else if (jqXHR.status == 404) alert('Requested file not found (404).');
            else if (jqXHR.status == 400) alert('Bad request (400).');
            else if (jqXHR.status == 500) alert('Internal Server Error (500).');
            else if (exception === 'parsererror') alert('Requested JSON parse failed.'); // некорректный ввод post-params => return в .php, нет данных
            else if (exception === 'timeout') alert('Time out error.'); // сервер завис?
            else if (exception === 'abort') alert('Ajax request aborted.');
            else alert('Uncaught Error. ' + jqXHR.responseText);
        }
    });
}

// удаление файла и перезагрузка модели
function modelDeleteFile(file_id) {
    $.ajax({
        url: '/files/'+file_id,
        method: 'delete',
        async: false,
        contentType: 'application/json',
        headers: {'Authorization': 'Bearer '+getCookie('token')},
        // data: JSON.stringify({}),
        success: function(data){
            modelGetFoldersAndFiles(modelData.current_folder.id);
            viewChangeFolder();
        },
        error: function (jqXHR, exception) {
            if (jqXHR.status === 0) alert('Not connect. Verify Network.');
            else if (jqXHR.status == 401) logoutOnAuthError();
            else if (jqXHR.status == 404) alert('Requested file not found (404).');
            else if (jqXHR.status == 400) alert('Bad request (400).');
            else if (jqXHR.status == 500) alert('Internal Server Error (500).');
            else if (exception === 'parsererror') alert('Requested JSON parse failed.'); // некорректный ввод post-params => return в .php, нет данных
            else if (exception === 'timeout') alert('Time out error.'); // сервер завис?
            else if (exception === 'abort') alert('Ajax request aborted.');
            else alert('Uncaught Error. ' + jqXHR.responseText);
        }
    });
}

//---------- ----------
// используем модель для обновления информации на странице (VIEW)
//---------- ----------

var viewData = {
    selected_file_id: null,
};

// Получение иконки для файла
function viewGetFileIcon(content_type) {
    type = '';
    if (content_type.substring(0, 6) == 'image/')
        type = 'image';
    else if (content_type == 'application/pdf')
        type = 'pdf';
    else if (content_type.substring(0, 6) == 'audio/')
        type = 'audio';
    const icons = {
        pdf: 'fas fa-file-pdf',
        image: 'fas fa-file-image',
        audio: 'fas fa-file-audio',
        default: 'fas fa-file'
    };
    return icons[type] || icons.default;
}

// отключение доступа к кнопкам переименования и удаления файлов
function disableFileButtons() {
    viewData.selected_file_id = null;
    $('#btn_rename, #btn_delete, #btn_open, #btn_share').each(function(index, element){
        $(this).addClass("disabled-button");
    });
}

// включение доступа к кнопкам переименования и удаления файлов
function enableFileButtons(file_id) {
    viewData.selected_file_id = file_id;
    $('#btn_rename, #btn_delete, #btn_open, #btn_share').each(function(index, element){
        $(this).removeClass("disabled-button");
    });
}

// вызывается при клике на папку
function onSelectFolder(folder_id){
    modelGetFoldersAndFiles(folder_id);
    viewChangeFolder();
    disableFileButtons();
}

// вызывается при двойном клике на файл
function onSelectFile(file_id){
    file = modelData.files.find((file) => {
        return file.id == file_id;
    });
    if (!(file === undefined))
        window.open('filedata.php?url='+file.url_filename, '_blank').focus();
}

// вызывается при одинарном клике на файл
function onClickFile(file_id){
    $('div.file-item').each(function(index, element){
        $(this).removeClass("file-selected");
    });
    $('div.file-item:hover').addClass("file-selected");
    enableFileButtons(file_id);
}

// Нажатие на кнопку создания папки
function onCreateNewFolder() {
    const name = prompt('Введите название папки:');
    if (!name) return;
    modelCreateFolder(name);
}

// Нажатие на кнопку загрузки файла
function onUploadFile() {
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

// Вызывается при нажатии на кнопку открытия файла
function onOpenFile() {
    var btn = $('#btn_open');
    $('#btn_open.disabled-button').each(function(){ btn = undefined; });
    if (btn === undefined) return;
    if (viewData.selected_file_id === null) return;
    onSelectFile(viewData.selected_file_id);
}

// Вызывается при нажатии на кнопку расшаривания файла
function onShareFile() {
    var btn = $('#btn_share');
    $('#btn_share.disabled-button').each(function(){ btn = undefined; });
    if (btn === undefined) return;
    if (viewData.selected_file_id === null) return;

    var file = modelFindFileById(viewData.selected_file_id);
    if (file === null) return;
    if (file.share.public) return;
    
    var answer = window.confirm("Уверены, что хотите поделиться файлом?");
    if (!answer) return;

    modelShareFileToPublic(viewData.selected_file_id);
}

// вызывается при переименовании файла
function onRenameFile() {
    var btn = $('#btn_rename');
    $('#btn_rename.disabled-button').each(function(){ btn = undefined; });
    if (btn === undefined) return;
    if (viewData.selected_file_id === null) return;

    var file = modelFindFileById(viewData.selected_file_id);
    if (file === null) return;

    const name = prompt('Введите название файла:', file.original_filename);
    if (!name) return;
    modelRenameFile(viewData.selected_file_id, name);
    disableFileButtons();
}

// вызывается при удалении файла
function onDeleteFile() {
    var btn = $('#btn_delete');
    $('#btn_delete.disabled-button').each(function(){ btn = undefined; });
    if (btn === undefined) return;
    if (viewData.selected_file_id === null) return;

    var answer = window.confirm("Уверены, что хотите удалить файл?");
    if (!answer) return;

    modelDeleteFile(viewData.selected_file_id);
    disableFileButtons();
}

// обновляет содержимое страницы
function viewChangeFolder(){
    // обновляем содержимое страницы
    // отрисовка папок
    const tree = document.getElementById('folderTree');
    if (modelData.current_folder.parent === null) {
        tree.innerHTML = "";
        $('div.sidebar h2').html('Домашняя папка');
    }
    else {
        $('div.sidebar h2').html(modelData.current_folder.name);
        tree.innerHTML = `
            <li class="folder-item" onclick="onSelectFolder('${modelData.current_folder.parent}')">
                <i class="fas fa-folder"></i> ..
            </li>`
    }
    tree.innerHTML += modelData.folders.map(folder => `
        <li class="folder-item" onclick="onSelectFolder(${folder.id})">
            <i class="fas fa-folder"></i> ${folder.name}
        </li>
    `).join('');
    // отрисовка файлов
    const grid = document.getElementById('fileGrid');
    grid.innerHTML = modelData.files.map(file => `
        <div class="file-item ${file.share.public?"file-shared":""}" ondblclick="onSelectFile(${file.id})" onclick="onClickFile(${file.id})">
            <i class="${viewGetFileIcon(file.content_type)} file-icon"></i>
            <div>${file.original_filename}</div>
        </div>
    `).join(''); 
}
