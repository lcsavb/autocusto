from django.shortcuts import render

def cadastro(request):
    return render(request, 'processos/cadastro.html')