import json
from django.shortcuts import render

from .plugins import plugins

def index(request):
    context = {"version": "0.7.0", "plugins": plugins}
    return render(request, 'web/place.html', context)
