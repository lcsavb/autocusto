(() => {
    const addMed = document.querySelector('#add-med');

    addMed.addEventListener('click', function (event) {
        const medSel = document.querySelector('#medicamentos-tab').children;
        const listaMedSel = Array.from(medSel);
        const medicamento = document.querySelector('#medicamentos').children;
        const listaMedicamentos = Array.from(medicamento);
        for (let n = 0; n < medSel.length; n++) {
            if (medSel[n].classList.contains('d-none')) {
                event.preventDefault();
                const medicamentoVinculado = document.querySelector(`#medicamento-${n}`);


                listaMedSel.forEach(element => {
                    if (element !== medSel[n]) {
                        element.classList.remove('active');
                        medicamentoVinculado.classList.remove('active');
                        medicamentoVinculado.classList.remove('show');

                    }
                    listaMedicamentos.forEach(element => {
                        if (element !== medicamentoVinculado) {
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

        posologiaPrimeiroMes.keyup(function () {
            if (botaoRepetirPosologia.val() == 'True') {
                posologiaSegundoMes.val(posologiaPrimeiroMes.val());
                posologiaTerceiroMes.val(posologiaPrimeiroMes.val());
            }
        });

        qtdPrimeiroMes.keyup(function () {
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


})();
