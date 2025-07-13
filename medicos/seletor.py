

def medico(usuario_ativo):
    if usuario_ativo.is_medico:
        medico = usuario_ativo.medicos.first()
        return medico
    else:
        pass
