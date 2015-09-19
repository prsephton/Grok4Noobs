//_____________________________________________________________________________________
// Javascript to move and re-order menu items.
//   Initial state, are a bunch of ul.menu > li.movable items.
//   When we click on one of them, we remove the .movable from all of them, and set
//   the clicked one to li.moving.  The items above we set to li.aboveme, and the
//   items below, we set to li.belowme.  When an li.aboveme is clicked, we move the
//   li.moving item to be above the clicked element.  The opposite for li.belowme.
//   When the li.moving item has moved, we remove aboveme, belowme and moving, and
//   set all the classes back to movable.

$(document).ready(function(){
    $('li.menuItem.setItemOrder').on('click', function(clickEvent){
        var setOrder = [];
        clickEvent.preventDefault();
        $('span.navTitle', $('li.menuItem.movable')).each(function(){
            setOrder.push($(this).text());
        });

        $('<div />').load('setOrder', {'new_order':JSON.stringify(setOrder)},
                                        function(response, status, xhr){
            console.log('response is ' + response);
            if (status != 'error') {
                document.location.href = '../';
            } else {
                alert(response);
            }
        });
    });

    $('ul.menu').on('click', '> li.movable, >li.aboveMe, >li.belowMe', function(){
        var parent = $(this).parent();
        var siblings = parent.children();

        function resetState(){
            siblings = parent.children();
            siblings.removeClass('moving').addClass('movable');
            siblings.removeClass('aboveMe').removeClass('belowMe');
        }

        if ($(this).hasClass('movable')) {
            var toMove = $(this);
            var idx = toMove.index();

            siblings.removeClass('movable');
            toMove.addClass('moving');

            if (idx > 0) {
                siblings.slice(0, idx).addClass('aboveMe');
            }
            if (idx < siblings.length) {
                siblings.slice(idx+1).addClass('belowMe');
            }
        } else {
            var toMove = $('li.moving', parent);
            if ($(this).hasClass('aboveMe')) {
                toMove.remove();
                $(this).before(toMove);
                resetState();
            }
            if ($(this).hasClass('belowMe')) {
                toMove.remove();
                $(this).after(toMove);
                resetState();
            }
        }
    });
});
