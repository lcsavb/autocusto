'use strict';

// (() => {

// Campo de tratamento prévio 
const tratou = $('#id_tratou');
const preenchidoPor = $('#id_preenchido_por');
const campoDezoito = $('.campo-18');
const input = campoDezoito.firstElementChild.firstElementChild.nextElementSibling.firstElementChild;

$(function() {
    if (preenchidoPor.val() == 'medico') {
        campoDezoito.removeClass('d-none');
        input.attr('required','');
    }
  });








// })();