from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'armageddon_system/index.html',{'msg':'test'})