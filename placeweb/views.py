"""Django views for PLACE"""
import json
import pkg_resources
from django.http import HttpResponse
from django.core.files import File
from django.shortcuts import render
from place import experiment
from .plugins import plugins
from .models import Experiment

def index(request):
    """PLACE main view"""
    version = pkg_resources.require("place")[0].version
    context = {"version": version, "plugins": plugins}
    return render(request, 'placeweb/place.html', context)

def submit(request):
    """Add an experiment to the PLACE queue (db)"""
    new_experiment = Experiment.objects.create() # pylint: disable=no-member
    new_experiment.config.save('config.json', File(request))
    return HttpResponse(json.dumps(experiment.QUEUED))

def status(request): # pylint: disable=unused-argument
    """Check status of PLACE"""
    return HttpResponse(json.dumps(experiment.status()))

#def liveplot(request):
#    """Get plot data (as bytes) for the requested instrument class"""
    #request_details = json.loads(request.body())
    #class_name = request_details['class_name']
    #data = experiment.get_liveplot_bytes(class_name)
    #return HttpResponse(data, content_type='application/octet-stream')
