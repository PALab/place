"""Django views for PLACE"""
import io
import os.path
import json
import zipfile

import pkg_resources
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.static import serve
from django.shortcuts import render

from . import worker
from .plugins import INSTALLED_PLACE_PLUGINS


def index(request):
    """PLACE main view"""
    version = pkg_resources.require("place")[0].version
    context = {"version": version, "plugins": INSTALLED_PLACE_PLUGINS}
    return render(request, 'placeweb/place.html', context)


def submit(request):
    """Add an experiment to the PLACE queue (db)"""
    experiment_id = 0
    directory = '{}/experiments/{:06d}/'.format(
        settings.MEDIA_ROOT, experiment_id)
    while os.path.exists(directory):
        experiment_id += 1
        directory = '{}/experiments/{:06d}/'.format(
            settings.MEDIA_ROOT, experiment_id)
    config = json.load(request)
    config['directory'] = directory
    worker.start(config)
    return JsonResponse(worker.status())


def status(request):  # pylint: disable=unused-argument
    """Check status of PLACE"""
    return JsonResponse(worker.status())


def history(request):  # pylint: disable=unused-argument
    """Get summary of experiments stored on the server"""
    experiment_entries = []
    path = '{}/experiments/'.format(settings.MEDIA_ROOT)
    for item in os.listdir(path):
        try:
            with open(os.path.join(path, item, 'config.json')) as file_p:
                config = json.load(file_p)
            experiment_entry = {}
            experiment_entry['version'] = config['metadata']['PLACE_version']
            experiment_entry['timestamp'] = config['metadata']['timestamp']
            experiment_entry['title'] = config['title']
            experiment_entry['comments'] = config['comments']
            experiment_entry['location'] = item
            experiment_entries.append(experiment_entry)
        except FileNotFoundError as err:
            print('config.json missing: {}'.format(err))
        except KeyError as err:
            print('Experiment in {} is missing config values: {}'.format(
                os.path.join(path, item), err))
    return JsonResponse({'experiment_entries': experiment_entries})


def download(request, location):  # pylint: disable=unused-argument
    """Download experiment data"""
    stream = io.BytesIO()
    zipf = zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED)
    zipf.write(os.path.join(
        settings.MEDIA_ROOT, "experiments", location, 'config.json'),
        arcname='config.json')
    zipf.write(os.path.join(
        settings.MEDIA_ROOT, "experiments", location, 'data.npy'),
        arcname='data.npy')
    zipf.close()
    response = HttpResponse(stream.getvalue())
    response['content_type'] = 'application/zip'
    response['Content-Disposition'] = 'attachement;filename=data.zip'
    stream.close()
    return response


def delete(request):
    """Delete experiment data"""
    location = json.load(request)['location']
    os.remove(os.path.join(
        settings.MEDIA_ROOT, "experiments", location, 'config.json'))
    os.remove(os.path.join(
        settings.MEDIA_ROOT, "experiments", location, 'data.npy'))
    os.rmdir(location)
    return history(request)


def progress_plots(request, path):
    """Get a PNG plot"""
    print('request for {}'.format(os.path.join(
        settings.MEDIA_ROOT, 'figures/progress_plot', path)))
    serve(request, 'figures/progress_plot/' + path,
          document_root=settings.MEDIA_ROOT)
