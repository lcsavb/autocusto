(() => {
    const mostrarProtocolo = $('#mostrar-protocolo');
    const protocolLink = $('#protocol-link');
    const overlay = $('#overlay');
    
    // Handle old floating button (if exists)
    mostrarProtocolo.click(() => {
        overlay.css('display','block');
        $('.consulta-protocolo').addClass('d-none');
    });

    // Handle new header protocol link
    protocolLink.click((e) => {
        e.preventDefault();
        overlay.css('display','block');
    });

    overlay.click(() => {
        overlay.css('display', 'none');
        $('.consulta-protocolo').removeClass('d-none');
    });

})();    
    

