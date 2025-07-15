(() => {
    const mostrarProtocolo = $('#mostrar-protocolo');
    const overlay = $('#overlay');
    
    mostrarProtocolo.click(() => {
        overlay.css('display','block');
        $('.consulta-protocolo').addClass('d-none');
    });

    overlay.click(() => {
        overlay.css('display', 'none');
        $('.consulta-protocolo').removeClass('d-none');
    });


})();    
    

