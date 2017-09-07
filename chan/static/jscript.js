function popup(text){
    $('.popup').text(text);
    setTimeout ("$('.popup').show('drop');", 1);
    setTimeout ("$('.popup').hide('drop');", 2500);
}

/*function sendPost(threadId, token){   
    $.ajax({
        url : '/createpost/',
        type : 'POST',
        data : {
            message: function() { return $("textarea[name=message]").val(); },
            mail: function() { return $("input[name=mail]").val(); },
            sage: function() { 
                if ($("input[name=sage]").prop('checked')) {
                    return 1;
                } else {
                    return 0;
                } 
            },
            csrfmiddlewaretoken: token,
            thread_id: threadId,
        },
        success : function(data){
            popup(data['message']);
        },
    });
};

$("input[type='submit']").click(function() { return false; }); //disable page reload
*/

$(document).ready(function() {
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
});

