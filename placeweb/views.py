"""Django views for PLACE"""
import json

import pkg_resources
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import render

from place import experiment

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
    directory = '{}/{}/'.format(settings.MEDIA_ROOT,
                                new_experiment.experiment_id)
    config_data = json.load(request)
    config_data['directory'] = directory
    new_experiment.config.save(
        name='config.json', content=ContentFile(json.dumps(config_data)))
    return JsonResponse({'status': experiment.QUEUED})


def status(request):
    """Check status of PLACE"""
    return JsonResponse({'status': experiment.status()})

# def liveplot(request):
#    """Get plot data (as bytes) for the requested instrument class"""
    # request_details = json.loads(request.body())
    # class_name = request_details['class_name']
    # data = experiment.get_liveplot_bytes(class_name)
    # return HttpResponse(data, content_type='application/octet-stream')
