$(document).ready(function(){
    $('body') .css({'padding-top': (($('.navbar-fixed-top').height()) + 1 )+'px'});
    $(window).resize(function(){
        $('body') .css({'padding-top': (($('.navbar-fixed-top').height()) + 1 )+'px'});
    });
});
