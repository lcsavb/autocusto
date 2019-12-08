'use static';

$(document).ready(function() {
	
	$('[data-toggle="tooltip"]').tooltip();

	orig = $.fn.css;
    $.fn.css = function() {
        var result = orig.apply(this, arguments);
        $(this).trigger('stylechanged');
        return result;
	}
	
});