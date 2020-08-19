$(document).ready(function() {
$('#id_data_1').mask('00/00/0000');
$('#id_altura').mask('000', {reverse:true});
$('#id_peso').mask('000', {reverse:true});
$('#id_cpf_paciente').mask('000.000.000-00', {reverse: false});
$('#telefone').mask('(00) 0000.0000', {reverse:false});
$('#cep').mask('00000-000');
});