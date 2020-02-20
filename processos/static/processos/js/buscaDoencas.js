// const campoBusca = document.querySelector('#id_cid');



// campoBusca.addEventListener('keypress', async function () {
//     let palavraChave = campoBusca.value;
//     let listaResultados = document.querySelector('#resultados');
//     if (palavraChave.length > 2) {
//         let res = await fetch (`http://127.0.0.1:8000/processos/ajax/doencas?b=${palavraChave}`);
//         let lista = await res.json();
//         resultados = [];
//         for (resultado in lista) {
//             resultado = document.createElement('li');
//             listaResultados.appendChild(resultado);
//         }

//     }
// });


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
        $.each(data, function(key, value) {
            listaResultados.append('<li class="list-group-item link-class">'+value.cid+' | <span class="text-muted">'+value.nome+'</span></li>');
        });
   
    }
});

});


    
$('#resultados').on('click', 'li', function() {
    var click_text = $(this).text().split('|');
    $('#id_cid').val($.trim(click_text[0]));
    $("#resultados").html('');
    
});
   