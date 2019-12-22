postJSON = function(url,data){
    return $.ajax({url:url,data:JSON.stringify(data),type:'POST', contentType:'application/json'});
 };
String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1).toLowerCase();
}

var heroes = ["swamp","tim","arthur"]
for (var i = 0; i < heroes.length; i++) {
    var id = "#button_" + heroes[i];
    $(id).on('click',function(e) {
        e.preventDefault();
        var name = this.id.split("_")[1].capitalize();
        //alert("clicked on " + name);
        postJSON("list",{})
            .done(function(data) {
                // If you have a 200 OK status reply, that means you
                // completed the challenge. The token is in the body
                //alert("Sucess! Token: " + data);
                document.write("Sucess! Token: " + data);
            }).fail(function(resp,status) {
                alert("You have absolutely no rights to do that.");
            });
});
}
