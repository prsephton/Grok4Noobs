tinymce.PluginManager.add('gfncode', function(editor, url) {

    function addOrEdit(url) {
        var url = url || 'attach';
        var title = 'Modify Attachment';

        if (url=='attach') title = 'Insert Attachment';


        $('<div />').load(url, function(r, a , b) {

            var dlg = $(this).dialog({
                title: title,
                modal: true,
                width: 'auto',
                resizable: false,
            });

            function responseHandler(responseText, textStatus, xhr, $form){
                if (textStatus=='error') {                // retry- comms or other error in submission
                    alert('Could not reach the server; Please try again.');
                } else if (responseText.length) {
                    if ($('div.form-status', $(responseText)).length) {  // form had errors in submission
                        $(form).html($(responseText));
                    } else {  // Everything is great
                        tinymce.activeEditor.selection.setContent(responseText);
                        dlg.remove();
                    }
               } else {   // Cancelled
                    dlg.remove();
               }
            }

			var form = $('form', this);
			$(form).ajaxForm({
			    success: responseHandler,
			});
        });
    }

	editor.addCommand('gfncodeCmd', addOrEdit);

    editor.addButton( 'gfncode', {
        title: 'Add Attachment',
        image: url+'/highlight.jpg',
        cmd: 'gfncodeCmd',
    });

    editor.addMenuItem('gfncode', {
        text: 'Add Attachment',
        image: url+'/highlight.jpg',
        cmd: 'gfncodeCmd',
        context: 'insert',
    });

    editor.on('init', function(initEv){
        $(editor.getBody()).on("click", "div.attachment", function(clickEv){
            clickEv.preventDefault();
            var src = $(this).attr("src") + '/modify';
            editor.selection.select(this);
            addOrEdit(src);
        });
    });

});

