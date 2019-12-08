'use strict';

$(document).ready(function() {

	// toggle report field
	$('#first-time-yes').click(function() {

		$('#first-time-report-field')
			.css({
				display: 'block'
			})
			.prop('required', true)	
		;

	});
	
	$('#first-time-no').click(function() {

		$('#first-time-report-field')
			.css({
				display: 'none'
			})
			.prop('required', false)	
		;

	});

	// toggle responsible name field
	$('#incapable-yes').click(function() {

		$('#responsible-name-field')
			.css({
				display: 'block'
			})
			.prop('required', true)	
		;

	});
	
	$('#incapable-no').click(function() {

		$('#responsible-name-field')
			.css({
				display: 'none'
			})
			.prop('required', false)				
		;

	});

	for (let i = 0; i < 5; i++) {

		$(`#medicine-${i}-toggler`).click(function() {

			$(this)
				.css({
					display: 'none'
				})
			;

			$(`#medicine-${i + 1}`)
				.css({
					display: "block"
				})
			;

		});

	}

});