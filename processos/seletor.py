from django import forms
REPETIR_ESCOLHAS = [(True, 'Sim'), (False, 'Não')]

def gerador_escolhas_numericas(min_n, max_n):
    ESCOLHAS = []
    while min_n <= max_n:
        ESCOLHAS.append((min_n,min_n))
        min_n += 1
    return ESCOLHAS


def seletor_campos(protocolo):
        if protocolo.nome == 'esclerose_multipla':
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
        elif protocolo.nome == 'dor':
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
        elif protocolo.nome == 'alzheimer':
            campos = {'opt_ot1': forms.ChoiceField(label='Hora', initial=1,
                                choices=gerador_escolhas_numericas(0,1)),
                    'opt_ot2': forms.ChoiceField(label='Dia da semana', initial=0,
                                choices=gerador_escolhas_numericas(0,1)),
                    'opt_ot3': forms.ChoiceField(label='Dia do mês', initial=1,
                                choices=gerador_escolhas_numericas(0,1)),
                    'opt_ot4': forms.ChoiceField(label='Mês', initial=1,
                                choices=gerador_escolhas_numericas(0,1)),
                    'opt_ot5': forms.ChoiceField(label='Ano', initial=0,
                                choices=gerador_escolhas_numericas(0,1)),
                    'opt_oe1': forms.ChoiceField(label='Local', initial=1,
                                choices=gerador_escolhas_numericas(0,1)),
                    'opt_oe2': forms.ChoiceField(label='Bairro', initial=0,
                                choices=gerador_escolhas_numericas(0,1)),
                    'opt_oe3': forms.ChoiceField(label='Cidade', initial=1,
                                choices=gerador_escolhas_numericas(0,1)),
                    'opt_oe4': forms.ChoiceField(label='Estado', initial=1,
                                choices=gerador_escolhas_numericas(0,1)),
                    'opt_mi': forms.ChoiceField(label='Memória imediata', initial=1,
                                choices=gerador_escolhas_numericas(0,3)), # de 0 a 3
                    'opt_ac': forms.ChoiceField(label='Atenção e cálculo', initial=2,
                                choices=gerador_escolhas_numericas(0,5)), # de 0 a 5
                    'opt_me': forms.ChoiceField(label='Memória de Evocação', initial=0,
                                choices=gerador_escolhas_numericas(0,3)), # 0 a 3
                    'opt_n': forms.ChoiceField(label='Nomeação', initial=1,
                                choices=gerador_escolhas_numericas(0,2)), # de 0 a 2
                    'opt_r': forms.ChoiceField(label='Repetição', initial=1,
                                choices=gerador_escolhas_numericas(0,1)), 
                    'opt_ce': forms.ChoiceField(label='Comando escrito', initial=1,
                                choices=gerador_escolhas_numericas(0,1)), # 0 ou 1
                    'opt_cv': forms.ChoiceField(label='Comando verbal', initial=1,
                                choices=gerador_escolhas_numericas(0,1)), # 0 a 3
                    'opt_f': forms.ChoiceField(label='Escrever frase', initial=1,
                                choices=gerador_escolhas_numericas(0,1)),
                    'opt_d': forms.ChoiceField(label='Desenho', initial=1,
                                choices=gerador_escolhas_numericas(0,1)),
                    'opt_total': forms.ChoiceField(label='Total MEEM', initial=16,
                                choices=gerador_escolhas_numericas(0,30)),
                    'opt_cdr': forms.ChoiceField(label='CDR', initial=1,
                                choices=gerador_escolhas_numericas(0,1))

                    }

        else:
            campos = {}
        return campos