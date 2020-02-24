from django import forms
REPETIR_ESCOLHAS = [(True, 'Sim'), (False, 'Não')]

def gerador_escolhas_numericas(min_n, max_n):
    ESCOLHAS = []
    while min_n <= max_n:
        ESCOLHAS.append((min_n,min_n))
        min_n += 1
    return ESCOLHAS




def seletor_campos(protocolo):
        if protocolo.nome == 'Esclerose Múltipla':
            campos = {'opt_edss': forms.ChoiceField(label='EDSS',
                    choices=[('0','0'),
                            ('1','1'),
                            ('1,5','1,5'),
                            ('2','2'),
                            ('2,5','2,5'),
                            ('3', '3'),
                            ('3,5','3,5'),
                            ('4', '4'),
                            ('4,5','4,5'),
                            ('5','5'),
                            ('5,5','5,5'),
                            ('6','6'),
                            ('6.5','6.5'),
                            ('7','7'),
                            ('7,5','7,5'),
                            ('8','8'),
                            ('8,5','8,5'),
                            ('9','9'),
                            ('9,5','9,5'),
                            ('10','10')
                            ],
                    widget=forms.Select(attrs={'class':'custom-select'}))
                    }
        elif protocolo.nome == 'Dor crônica':
            campos = {'opt_eva': forms.ChoiceField(label='EVA', initial=10,
                                choices=gerador_escolhas_numericas(4,10),
                                widget=forms.Select(attrs={'class':'custom-select'})),
                    'opt_lanns': forms.ChoiceField(label='LANNS', initial='24',
                                widget=forms.Select(attrs={'class':'custom-select'}),
                                choices=[('5','5'),
                                        ('10','10'),
                                        ('13', '13'),
                                        ('15', '15'),
                                        ('16','16'),
                                        ('21','21'),
                                        ('24', '24')])
                    }

            # dados_dor = {
#     'eva': '5', ## de 4 a 10
#     'lanns_escore': '24' ## depois completar com as categorias individuais
# }

        else:
            campos = []
        return campos