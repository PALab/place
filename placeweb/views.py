"""Django views for PLACE"""
import os.path
import json

import pkg_resources
from django.conf import settings
from django.http import JsonResponse
from django.views.static import serve
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


def progress_plots(request, path):
    """Get a PNG plot"""
    print('request for {}'.format(os.path.join(
        settings.MEDIA_ROOT, 'figures/progress_plot', path)))
    serve(request, 'figures/progress_plot/' + path,
          document_root=settings.MEDIA_ROOT)
