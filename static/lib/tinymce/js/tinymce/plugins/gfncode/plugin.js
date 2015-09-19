tinymce.PluginManager.add('gfncode', function(editor, url) {
    alert('url is:' + url);
    // Adds a menu item to the insert menu
    editor.addMenuItem('gfncode', {
        text: 'Formatted Source Code',
        context: 'insert',
        onclick: function() {
            // Open window with a specific url
            editor.windowManager.open({
                title: 'Insert Formatted Source Code',
                url: 'pygmentize',
                width: 800,
                height: 600,
                buttons: [{
                    text: 'Close',
                    onclick: 'close'
                }]
            });
        }
    });
});

