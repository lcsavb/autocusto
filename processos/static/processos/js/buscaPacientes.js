(() => {

const campoBusca = $('#id_cpf_paciente');
const listaPacientes = $('#pacientes');
const form = $('#js-form')

campoBusca.keyup(function(event) {
    let palavraChave = $(this).val();
    let url = form.attr('data-busca-pacientes');

    $.ajax({
        url: url,
        data: {'palavraChave': palavraChave},
        dataType: 'json',
        success: function(data) {
            listaPacientes.empty();
            if (data.length == 0) {
                listaPacientes.append('<li class="list-group-item link-class">Nenhum resultado encontrado</span></li>');
            } else {
                $.each(data, function(key, value) {
                    if (palavraChave.length > 2) {
                        listaPacientes.append('<li class="list-group-item link-class">'+value.cpf_paciente+' | <span class="text-muted">'+value.nome_paciente+'</span></li>');
                    }
                });
                
            }
       
        }
    });
    
    });

    $('#pacientes').on('click', 'li', function() {
        var click_text = $(this).text().split('|');
        $('#id_cpf_paciente').val($.trim(click_text[0]));
        $("#pacientes").html('');
        
    });

})();