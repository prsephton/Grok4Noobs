$(document).ready(function(){
    $('div.attachment').on('click', function(e){
        e.preventDefault();
    });
    $('div.attachment').each(function(){
        var attach = $(this);
        $("<div />").load(attach.attr('src')+'/highlight', function(){
            attach.html($(this).html());
        });
    });
});