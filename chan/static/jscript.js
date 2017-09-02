function sendPost(token){
    
    $.ajax({
        url : 'createpost/',
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
        },
        success: function(data){
            alert( data['message'] );
        },
    });
};