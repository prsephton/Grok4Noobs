// Popup dialogs when one clicks on a div.popup

$(document).ready(function(){
    $('div.popup').on('click', function(e){
        e.preventDefault();
        var href = $('a', this).attr('href');
        var title = $(this).attr('title');
        $('<div />').load(href, function(r, a , b) {
            $(this).dialog({
                title: title,
                modal: true,
                width: 'auto',
                resizable: false,
            });
        });
    });
});