'use strict';

const isTratado = document.getElementById('id_tratou');
const divTratPrevio = document.getElementById('trat-escondido');
const campoTrat = divTratPrevio.firstElementChild.firstElementChild.nextElementSibling.firstElementChild;
const isIncapaz = document.getElementById('id_incapaz');
const divResponsavel = document.getElementById('resp-escondido');
const campoIncapaz = divResponsavel.firstElementChild.firstElementChild.nextElementSibling.firstElementChild;
const campoDezoito = document.querySelector('#id_preenchido_por');
const divCampoDezoito = document.querySelectorAll('.campo-18');



function mostrarCampo(escolha,divAlvo,campoAlvo) {
    if (escolha.value === 'True') {
        divAlvo.classList.remove('d-none');
        campoAlvo.setAttribute('required', '');
    }
    else {
        divAlvo.classList.add('d-none');
        campoAlvo.removeAttribute('required', '');
}

}

isTratado.addEventListener('ValueChange', () => {mostrarCampo(isTratado,divTratPrevio,campoTrat)});
isIncapaz.addEventListener('ValueChange', () => {mostrarCampo(isIncapaz,divResponsavel,campoIncapaz)});
campoDezoito.addEventListener('ValueChange', function() {
    if (campoDezoito.value == 'medico') {
        for (let n = 0; divCampoDezoito.length; n++) {
            divCampoDezoito[n].classList.remove('d-none');
            divCampoDezoito[n].firstElementChild.firstElementChild.nextElementSibling.firstElementChild.setAttribute('required', '');
        }
    }
    else {
        for (let n = 0; divCampoDezoito.length; n++) {
            divCampoDezoito[n].classList.add('d-none');
            divCampoDezoito[n].firstElementChild.firstElementChild.nextElementSibling.firstElementChild.removeAttribute('required', '');
        } 
    }

});