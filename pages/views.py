from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def home(request):
    context = {'subtitle': '<h2>Know Your Surroundings</h2>'}
    return render(request, 'home.html', context)

