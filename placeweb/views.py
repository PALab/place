import json
from django.http import HttpResponse
from django.shortcuts import render
from place.experiment import start as start_experiment, __version__

from .plugins import plugins

def index(request):
    context = {"version": __version__, "plugins": plugins}
    return render(request, 'placeweb/place.html', context)

def start(request):
    print(request.body)
    start_experiment(json.loads(request.body))
    return HttpResponse(json.dumps('started'))
