function popup(text){
    $('.popup').text(text);
    setTimeout ("$('.popup').show('drop');", 1);
    setTimeout ("$('.popup').hide('drop');", 2500);
}

function refresh() { //Refresh threads
    console.log('refresh');
    $.get( "getposts/", function( data ) {
        $( "#container" ).html( data );
        bindButtonClick();
      });  
}

function bindButtonClick() {
    //Post id link click
    $(".idlink").click(function () {
        var text = $("#mfield").val();
        $("#mfield").val(text + ">>" + $(this).text());
        $("#mfield").focus();
    });

    //Full image
    $('.postimg').click(function() {
        $('#fullscreen').show();
        $('#img01').attr('src', $(this).attr('src'));
    });

    window.onclick = function(event) {
        if (event.target == document.getElementById('fullscreen')) {
        $('#fullscreen').hide();
        }
    }

    $('#fullscreen').click(function() {
        $('#fullscreen').hide();
    });
}

function sendPost(token){
    var files = $('input[type=file]').files;    
    var form = document.forms.namedItem("postform");
    var formData = new FormData(form);
    var request = new XMLHttpRequest();

    request.open('POST', 'createpost/');
    request.onreadystatechange = function() {
        if (request.readyState == 4) {
           if(request.status == 200) {
             popup(JSON.parse(request.responseText)['message']);
             if(JSON.parse(request.responseText)['allow_post']) { //Only if post is sent
                refresh(); 
                $("#mfield").val( '' );
             }
               
      };
    }};
    request.send(formData);   
};

$(document).ready(function() {
    $("#refreshBtn").click(function () {
        var old_count = $( ".post" ).length;
        refresh();
        var new_count = $( ".post" ).length;
        popup( new_count - old_count + " new posts ");
    });

    bindButtonClick();

     //BBCODES   
     $("#boldBtn").click(function () {
        var text = $("#mfield").val();
        $("#mfield").val( text + "[b][/b]" );
        $("#mfield").focus();
    });
    $("#iBtn").click(function () {
        var text = $("#mfield").val();
        $("#mfield").val( text + "[i][/i]" );
        $("#mfield").focus();
    });
    $("#ulineBtn").click(function () {
        var text = $("#mfield").val();
        $("#mfield").val( text + "[u][/u]" );
        $("#mfield").focus();
    });
    $("#spBtn").click(function () {
        var text = $("#mfield").val();
        $("#mfield").val( text + "[s][/s]"  );
        $("#mfield").focus();
    });
});

