//  If placeholder is supported, use it in forms
jQuery.support.placeholder = (function(){
	var i = document.createElement('input'); return 'placeholder' in i;
})();

$(document).ready(function(){
	if ($.support.placeholder) {
		$('tr.form-widget').each(function(){
			var lb = $('td.label', this);
			var fld = $('input, textarea', this);
			var required = false;
			if (fld.length > 0) {
				var labels = $('span', lb);
				if (labels.length==2){
					labels = labels.slice(1);
					required = true;
				}
				if (labels.length) {
					var txt = labels.text();
					fld.attr('placeholder', txt);
					if (required) fld.addClass('required');
					lb.css("display", "none");
				}
			}
		});
	}
});