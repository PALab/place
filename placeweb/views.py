"""Django views for PLACE"""
import json
import pkg_resources
from django.http import HttpResponse
from django.shortcuts import render
from place import experiment
from .plugins import plugins

def index(request):
    """PLACE main view"""
    version = pkg_resources.require("place")[0].version
    context = {"version": version, "plugins": plugins}
    return render(request, 'placeweb/place.html', context)

def start(request):
    """PLACE start experiment POST"""
    return HttpResponse(json.dumps(experiment.start(json.loads(request.body))))

def status(request): # pylint: disable=unused-argument
    """Check status of PLACE"""
    return HttpResponse(experiment.status())
