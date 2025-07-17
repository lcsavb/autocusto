from django import forms


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