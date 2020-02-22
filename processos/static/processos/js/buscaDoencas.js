(() => {
const campoBusca = $('#id_cid');
let listaResultados = $('#resultados');

campoBusca.keyup(function (event) {
    event.preventDefault();

    let palavraChave = $(this).val();

    let url = `http://127.0.0.1:8000/processos/ajax/doencas?b=${palavraChave}`;

$.ajax({
    url: url,
    data: {'palavraChave': palavraChave},
    dataType: 'json',
    success: function(data) {
        listaResultados.empty();
        if (data.length == 0) {
            listaResultados.append('<li class="list-group-item link-class">Nenhum resultado encontrado</span></li>');
        } else {
            $.each(data, function(key, value) {
                if (palavraChave.length > 2) {
                    listaResultados.append('<li class="list-group-item link-class">'+value.cid+' | <span class="text-muted">'+value.nome+'</span></li>');
                }
            });
            
        }
   
    }
});

});


    
$('#resultados').on('click', 'li', function() {
    var click_text = $(this).text().split('|');
    $('#id_cid').val($.trim(click_text[0]));
    $("#resultados").html('');
    
});
   

})();
