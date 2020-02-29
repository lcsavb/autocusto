(() => {
    const campoPrimeiraVez = $('#id_consentimento');
    const url = $('#div_url_1_vez').attr('data-1-vez-url');
    const relatorio = $('.relatorio');
    const divRelatorio = $('#div-relatorio');
    const cid = $('#id_cid').val();

    campoPrimeiraVez.change(() => {
        let escolha = campoPrimeiraVez.val();
        escolha = escolha == 'True';
        if (escolha) {
            $.ajax ( {
                url: url,
                data: {'cid': cid},
                datatype: 'json',
                success: function(res) {
                    console.log(res);
                    if (res.relatorio) {
                        divRelatorio.removeClass('d-none');
                        relatorio.val(res.relatorio);
                    }
                }

            }
            );
        }
        else {
            divRelatorio.addClass('d-none');
            relatorio.val('');
        }
    });


    


})();
