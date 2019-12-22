function ascii (a) { return a.charCodeAt(0); }
function toChar(i) { return String.fromCharCode(i); }

function superencryption(msg,key) {
    if (key.length < msg.length) {
        var diff = msg.length - key.length;
        key += key.substring(0,diff);
    }

    var amsg = msg.split("").map(ascii);
    var akey = key.substring(0,msg.length).split("").map(ascii);
    return btoa(amsg.map(function(v,i) {
        return v ^ akey[i];
    }).map(toChar).join(""));
}

$('#loginForm').submit(function(e) {
    e.preventDefault();
    var mySecureOneTimePad = "Never send a human to do a machine's job";
    var username = $('#username').val();
    var password = $('#password').val();

    if (username.length > 100) {
        alert("There's a difference between knowing the path and walking the path.");
        return;
    } else if (password.length > 100) {
        alert("The best answer to anger is silence.");
        return;
    }
    var enc = superencryption(username,mySecureOneTimePad) ;
    if (enc != password) {
        alert("I didn't say it would be easy, Neo. I just said it would be the truth.");
        return;
    }
    postJSON = function(url,data){
        return $.ajax({url:url,data:JSON.stringify(data),type:'POST', contentType:'application/json'});
    };
    postJSON("ex1",{"user":username,"pass":password})
        .done(function(data) {
            //if you get a 200 OK status, that means you  successfully
            // completed the challenge. The token is in the body.
            ///alert("Sucess! Token: " + data)
            document.write("Sucess! Token: " + data);
        }).fail(function(resp,status) {
            alert("Pain is temporary. Quitting lasts forever.");
        });
});
