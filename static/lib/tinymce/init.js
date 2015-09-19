tinymce.init({
    selector: "textarea",
    content_css: "/fanstatic/mygrok.grok4noobs/mceStyle.css",
    plugins: ["code", "lists", "charmap", "paste", "gfncode", "textcolor", "link", "visualblocks", "table"],
    toolbar: 'undo redo | gfncode | link | styleselect | bold italic underline | ' +
    		 'alignleft aligncenter alignright alignjustify | ' +
    		 'bullist numlist outdent indent | forecolor backcolor',
    extended_valid_elements: "div[class|id|title|lang|style|align|onclick|name|src]",
    style_formats_merge: true,
    style_formats: [
        {  title: "Images", selector: 'img',
           items: [
              { title: 'Normal',        styles: {'float': 'none', 'margin': '10px', }},
              { title: 'Float Left',    styles: {'float': 'left', 'margin': '0 10px 0 10px'}},
              { title: 'Float Right',   styles: {'float': 'right','margin': '0 0 10px 10px'}},
            ]
        },
    ],

});
