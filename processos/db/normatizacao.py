
from processos.models import Protocolo
protocols = Protocolo.objects.all()
for protocol in protocols:
    name = protocol.nome
    print(name)
    adjusted_name = name.replace(' ', '_')
    adjusted_name_2 = adjusted_name.replace('-', '_')
    adjusted_name_3 = adjusted_name_2.replace(',', '_')
    adjusted_name_4 = adjusted_name_3.replace('á', 'a')
    adjusted_name_5 = adjusted_name_4.replace('é', 'e')
    adjusted_name_6 = adjusted_name_5.replace('í', 'i')
    adjusted_name_7 = adjusted_name_6.replace('ç', 'c')
    adjusted_name_8 = adjusted_name_7.replace('ã', 'a')
    adjusted_name_9 = adjusted_name_8.replace('ú', 'u')
    adjusted_name_10 = adjusted_name_9.replace('ê', 'e')
    adjusted_name_11 = adjusted_name_10.replace('ó', 'o')
    print(adjusted_name_11.lower())
    protocol.nome = adjusted_name_11.lower()
    protocol.save()
