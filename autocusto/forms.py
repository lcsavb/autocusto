from django import forms


# error report form
class ErrorReportForm(forms.Form):
    name = forms.CharField(
        label="Nome",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome (apenas para usuários não logados)'
        })
    )
    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu email (apenas para usuários não logados)'
        })
    )
    description = forms.CharField(
        label="Descrição do Erro",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Descreva o erro em detalhes...'
        })
    )
    steps = forms.CharField(
        label="Passos para Reproduzir",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': '1. Faça isso...\n2. Clique aqui...\n3. O erro acontece quando...'
        })
    )


# feature request form
class FeatureRequestForm(forms.Form):
    name = forms.CharField(
        label="Nome",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome (apenas para usuários não logados)'
        })
    )
    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu email (apenas para usuários não logados)'
        })
    )
    description = forms.CharField(
        label="Descrição da Funcionalidade",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Descreva a funcionalidade desejada em detalhes...'
        })
    )


# process feedback form
class ProcessFeedbackForm(forms.Form):
    name = forms.CharField(
        label="Nome",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome (apenas para usuários não logados)'
        })
    )
    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu email (apenas para usuários não logados)'
        })
    )
    processo_info = forms.CharField(
        label="Informações do Processo (Paciente, CID, etc.)",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: João Silva, CID M79.9, Data: 15/01/2024'
        })
    )
    feedback_type = forms.ChoiceField(
        label="Tipo de Problema",
        choices=[
            ('incompleto', 'Processo gerado incompleto'),
            ('incorreto', 'Informações incorretas no processo'),
            ('formato', 'Problema de formatação/layout'),
            ('outros', 'Outros problemas')
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    description = forms.CharField(
        label="Descrição do Problema",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Descreva o problema encontrado no processo...'
        })
    )