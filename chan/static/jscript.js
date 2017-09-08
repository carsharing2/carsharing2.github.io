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

function insertBbcode(startTag, closeTag) {
    var textArea = $("#mfield");
    var len = textArea.val().length;
    var start = textArea[0].selectionStart;
    var end = textArea[0].selectionEnd;
    var selectedText = textArea.val().substring(start, end);
    var replacement = startTag + selectedText + closeTag;
    textArea.val(textArea.val().substring(0, start) + replacement + textArea.val().substring(end, len));
    textArea.focus();
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

function sendPost(){
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
                    $("input[type=file]").replaceWith( $("input[type=file]").val('').clone(true)); //Reset file field after post
                }   
            } else {
                popup( 'Unknown error: status code ' + request.status);
            }
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
        insertBbcode('[b]', '[/b]');
    });
    $("#iBtn").click(function () {
        insertBbcode('[i]', '[/i]');
    });
    $("#ulineBtn").click(function () {
        insertBbcode('[u]', '[/u]');
    });
    $("#spBtn").click(function () {
        insertBbcode('[s]', '[/s]');
    });
});

