'use strict';
(() => {
const divTratPrevio = $('#trat-escondido');
const campoTrat = $('.cond-trat');
const divResponsavel = $('#resp-escondido');
const campoIncapaz = $('.cond-incapaz');
const divCampoDezoito = $('.campo-18');
const inputsCampoDezoito = $('.cond-campo-18');

function mostrarCampoRadio(radioName, divAlvo, campoAlvo) {
    const selectedValue = $(`input[name="${radioName}"]:checked`).val();
    
    if (selectedValue == 'True' || selectedValue == 'medico') {
        divAlvo.removeClass('d-none');
        campoAlvo.attr('required', ' ');
    }
    else {
        divAlvo.addClass('d-none');
        campoAlvo.removeAttr('required');
    }
}

$(document).ready (() => {
    // Initialize visibility based on current radio button selections
    mostrarCampoRadio('tratou', divTratPrevio, campoTrat);
    mostrarCampoRadio('incapaz', divResponsavel, campoIncapaz);
    mostrarCampoRadio('preenchido_por', divCampoDezoito, inputsCampoDezoito);
    
    // Set up event listeners for radio button changes
    $(document).on('change', 'input[name="tratou"]', () => {
        mostrarCampoRadio('tratou', divTratPrevio, campoTrat);
    });
    $(document).on('change', 'input[name="incapaz"]', () => {
        mostrarCampoRadio('incapaz', divResponsavel, campoIncapaz);
    });
    $(document).on('change', 'input[name="preenchido_por"]', () => {
        mostrarCampoRadio('preenchido_por', divCampoDezoito, inputsCampoDezoito);
    });
});


})();