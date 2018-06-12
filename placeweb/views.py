"""Django views for PLACE"""
import json

import pkg_resources
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

from . import worker
from .models import Experiment
from .plugins import plugins


def index(request):
    """PLACE main view"""
    version = pkg_resources.require("place")[0].version
    context = {"version": version, "plugins": plugins}
    return render(request, 'placeweb/place.html', context)


def submit(request):
    """Add an experiment to the PLACE queue (db)"""
    new_experiment = Experiment.objects.create()  # pylint: disable=no-member
    directory = '{}/experiments/{:06d}/'.format(settings.MEDIA_ROOT,
                                                new_experiment.experiment_id)
    config = json.load(request)
    config['directory'] = directory
    worker.start(config)
    return JsonResponse(worker.status())


def status(request):  # pylint: disable=unused-argument
    """Check status of PLACE"""
    return JsonResponse(worker.status())

# def liveplot(request):
#    """Get plot data (as bytes) for the requested instrument class"""
    # request_details = json.loads(request.body())
    # class_name = request_details['class_name']
    # data = experiment.get_liveplot_bytes(class_name)
    # return HttpResponse(data, content_type='application/octet-stream')
