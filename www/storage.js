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