'use strict';

$(document).ready(function() {

    const DATE_MASK_CLASS = '.date-mask';
    const MAX_DATE_LENGTH = 10;
    const ALLOWED_CHARACTERS = '0123456789';

    $(DATE_MASK_CLASS).change(function(event) {

        let text = $(this).val();

        switch (text.length) {

            case 2:
            case 5:
                text += '/';
                break;

        }

        $(this).val(text);

    });
    
    $(DATE_MASK_CLASS).keypress(function(event) {

        let text = $(this).val();
        let typedCharacter = String.fromCharCode(event.which);

        if (text.length > MAX_DATE_LENGTH || !ALLOWED_CHARACTERS.includes(typedCharacter)) {
            event.preventDefault();
        }
        
    });

});