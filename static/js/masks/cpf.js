'use strict';

$(document).ready(function() {

    const CPF_MASK_CLASS = '.cpf-mask';
    const MAX_CPF_LENGTH = 13;
    const ALLOWED_CHARACTERS = '0123456789';

    $(CPF_MASK_CLASS).change(function(event) {
        
        let text = $(this).val();
        
        switch (text.length) {

            case 3:
            case 7:
                currentText += '.';
                break;

            case 11:
                currentText += '-';
                break;
                
        }

        $(this).val(text);

    });

    $(CPF_MASK_CLASS).keypress(function(event) {

        let text = $(this).val();
        let typedCharacter = String.fromCharCode(event.which);
        
        if (text.length > MAX_CPF_LENGTH || !ALLOWED_CHARACTERS.includes(typedCharacter)) {
            event.preventDefault();
        }

    });

});