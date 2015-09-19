tinymce.PluginManager.add('gfncode', function(editor, url) {

	editor.addCommand('gfncodeCmd', function(){
		var win=editor.windowManager.open({
            title: 'Insert Highlighted Source Code',
            url: 'pygmentize',
            width:  600,
            height: 400,
            inline: true,
        },{
        	plugin_url: url,
        	win: window,
        });
		var iframe = $('iframe', win.getEl());
		iframe.load(function(){
			var body = $('body', iframe.contents());
			var form = $('form', body);
			$('input[type=submit]', form).on('click', function(clickEvent){
				var bn = $(clickEvent.target);
				bn.attr('checked', 'checked');
			});
			form.on('submit', function(e){
				e.preventDefault();
				var bn = $('input[type="submit"][checked="checked"]', form);
				bn.attr('type', 'checkbox');   // Bluff serialize()
				var frmData = $("input, textarea, select", form ).serialize();
				bn.attr('type', 'submit');

				var action = $(this).attr('action');
				$('<div />').load(action, data=frmData, function(responseText, textStatus, req){
					if (textStatus=='error') {                // retry- comms or other error in submission
						alert('Could not reach the server; Please try again.');
					} else if (responseText.length) {
						if ($('div.form-status', this).length) {  // form had errors in submission
							$(form).html($(this).html());
						} else {  // Everything is great
							tinymce.activeEditor.selection.setContent(responseText);
							win.close();
						}
					} else {   // Cancelled
						win.close();
					}
				});
			});
		});
	});

    editor.addButton( 'gfncode', {
        title: 'Highlight Source Code',
        image: url+'/highlight.jpg',
        cmd: 'gfncodeCmd',
    });

    editor.addMenuItem('gfncode', {
        text: 'Highlight Source Code',
        image: url+'/highlight.jpg',
        cmd: 'gfncodeCmd',
        context: 'insert',
    });



});

