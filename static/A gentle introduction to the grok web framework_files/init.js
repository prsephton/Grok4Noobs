tinymce.init({
    selector: "textarea",
    content_css: "/fanstatic/mygrok.grok4noobs/mceStyle.css",
    plugins: ["lists", "charmap", "paste", "gfncode", "textcolor", "link"],
    toolbar: 'undo redo | gfncode | link | styleselect | bold italic underline | ' +
    		 'alignleft aligncenter alignright alignjustify | ' +
    		 'bullist numlist outdent indent | forecolor backcolor'
});
