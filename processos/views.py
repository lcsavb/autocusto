from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required
def cadastro(request):
    return render(request, 'processos/cadastro.html')