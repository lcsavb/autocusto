from processos.models import Protocolo

protocolos = Protocolo.objects.all()

for protocolo in protocolos:
    nome = protocolo.nome
    print(nome)
    # nome_ajustado = nome.replace(' ', '_')
    # nome_ajustado_2 = nome_ajustado.replace('-','_')
    # nome_ajustado_3 = nome_ajustado_2.replace(',','_')
    # nome_ajustado_4 = nome_ajustado_3.replace('á','a')
    # nome_ajustado_5 = nome_ajustado_4.replace('é','e')
    # nome_ajustado_6 = nome_ajustado_5.replace('í','i')
    # nome_ajustado_7 = nome_ajustado_6.replace('ç','c')
    # nome_ajustado_8 = nome_ajustado_7.replace('ã','a')
    # nome_ajustado_9 = nome_ajustado_8.replace('ú','u')
    # nome_ajustado_10 = nome_ajustado_9.replace('ê','e')
    # nome_ajustado_11 = nome_ajustado_10.replace('ó','o')
    # print(nome_ajustado_11.lower())
    # protocolo.nome = nome_ajustado_11.lower()
    # protocolo.save()
