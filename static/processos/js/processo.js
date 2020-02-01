'use strict';

(() => {
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

// Checar campos condicionais no carregamento

function mostrarCampoDezoito (event) {
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

}

window.addEventListener("load", () => {mostrarCampo(isIncapaz,divResponsavel,campoIncapaz)});
window.addEventListener("load", () => {mostrarCampo(isTratado,divTratPrevio,campoTrat)});
window.addEventListener('load', mostrarCampoDezoito);

// Campos condicionais na mudança de valor
isTratado.addEventListener('ValueChange', () => {mostrarCampo(isTratado,divTratPrevio,campoTrat)});
isIncapaz.addEventListener('ValueChange', () => {mostrarCampo(isIncapaz,divResponsavel,campoIncapaz)});
campoDezoito.addEventListener('ValueChange', mostrarCampoDezoito);


// Medicamentos

const addMed = document.querySelector('#add-med');

addMed.addEventListener('click', function(event) {
    const medSel = document.querySelector('#medicamentos-tab').children;
    const listaMedSel = Array.from(medSel);
    const medicamento = document.querySelector('#medicamentos').children;
    const listaMedicamentos = Array.from(medicamento);
    for (let n = 0; n < medSel.length; n++) {
      if (medSel[n].classList.contains('d-none')) {
        event.preventDefault();
        const medicamentoVinculado = document.querySelector(`#medicamento-${n}`);

        
        listaMedSel.forEach(element => { if (element !== medSel[n]) {
            element.classList.remove('active');
            medicamentoVinculado.classList.remove('active');
            medicamentoVinculado.classList.remove('show');
            
            }
        listaMedicamentos.forEach(element => { if (element !== medicamentoVinculado) {
            element.classList.remove('active');
            element.classList.remove('show');
        }
        
        })
            
        });
        medSel[n].classList.remove('d-none');
        medSel[n].classList.add('active');
        medicamento[n].classList.toggle('active');
        medicamento[n].classList.toggle('show');
        

        break;
      } 
      else {
          event.preventDefault();
      }
    }
  });


  // Repetir posologia

  function repetirPosologia(numMed) {
    const botaoRepetirPosologia = $(`#id_med${numMed}_repetir_posologia`);
    const posologiaPrimeiroMes = $(`#id_med${numMed}_posologia_mes1`);
    const posologiaSegundoMes = $(`#id_med${numMed}_posologia_mes2`);
    const posologiaTerceiroMes = $(`#id_med${numMed}_posologia_mes3`);
    const qtdPrimeiroMes = $(`#id_qtd_med${numMed}_mes1`)
    const qtdSegundoMes = $(`#id_qtd_med${numMed}_mes2`)
    const qtdTerceiroMes = $(`#id_qtd_med${numMed}_mes3`)
    const divPosologiasOpcionais = $(`#posologias-opcionais-med${numMed}`)

    botaoRepetirPosologia.change(function () {
        divPosologiasOpcionais.toggleClass('d-none');
    });

        posologiaPrimeiroMes.keyup(function() {
            if (botaoRepetirPosologia.val() == 'True') {            
            posologiaSegundoMes.val(posologiaPrimeiroMes.val());
            posologiaTerceiroMes.val(posologiaPrimeiroMes.val());
            }            
        });

        qtdPrimeiroMes.keyup(function() {
            if (botaoRepetirPosologia.val() == 'True') {
            qtdSegundoMes.val(qtdPrimeiroMes.val());
            qtdTerceiroMes.val(qtdPrimeiroMes.val());
            }
        });

    }

  repetirPosologia(1);
  repetirPosologia(2);
  repetirPosologia(3);
  repetirPosologia(4);
  repetirPosologia(5);



  //// Edição completa
const edicaoCompleta = $('#id_edicao_completa');
const dadosRepetidos = $('#dados-repetidos');

edicaoCompleta.change(function() {
    dadosRepetidos.toggleClass('d-none');
});

})();