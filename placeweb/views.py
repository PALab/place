"""Django views for PLACE"""
import io
import os.path
import json
import time
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
    status = worker.status()
    if status['status'] == worker.READY:
        status['history'] = history()
    return JsonResponse(status)


def history():
    """Get summary of experiments stored on the server"""
    experiment_entries = []
    path = '{}/experiments/'.format(settings.MEDIA_ROOT)
    try:
        items = os.listdir(path)
    except FileNotFoundError:
        items = []
    for item in items:
        try:
            with open(os.path.join(path, item, 'config.json')) as file_p:
                config = json.load(file_p)
            experiment_entry = {}
            experiment_entry['version'] = config['metadata']['PLACE_version']
            experiment_entry['timestamp'] = config['metadata']['timestamp']
            experiment_entry['title'] = config['title']
            experiment_entry['comments'] = config['comments']
            experiment_entry['location'] = item
            experiment_entry['filename'] = _title_to_filename(config['title'])
            experiment_entries.append(experiment_entry)
        except FileNotFoundError as err:
            print('config.json missing: {}'.format(err))
        except KeyError as err:
            print('Experiment in {} is missing config values: {}'.format(
                os.path.join(path, item), err))
    return {'experiment_entries': sorted(experiment_entries, key=timestamp_to_millis, reverse=True)}


def timestamp_to_millis(entry):
    """Convert timestamps to milliseconds (if not already)"""
    if isinstance(entry['timestamp'], int):
        return entry['timestamp']
    # The following code is really only needed for
    # experiments created with PLACE prior to version 0.8
    return time.mktime(time.strptime(entry['timestamp'], r'%Y-%m-%d %H:%M:%S.%f'))


def download(request, location):  # pylint: disable=unused-argument
    """Download experiment data"""
    conf = os.path.join(settings.MEDIA_ROOT, "experiments",
                        location, 'config.json')
    with open(conf) as file_p:
        json_config_dat = json.load(file_p)
    stream = io.BytesIO()
    zipf = zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED)
    zipf.write(
        conf,
        arcname='config.json'
    )
    try:
        zipf.write(
            os.path.join(settings.MEDIA_ROOT, "experiments",
                         location, 'data.npy'),
            arcname='data.npy'
        )
    except FileNotFoundError:
        for i in range(1000):
            try:
                zipf.write(
                    os.path.join(
                        settings.MEDIA_ROOT,
                        "experiments",
                        location,
                        'data_{:03d}.npy'.format(i)
                    )
                )
            except FileNotFoundError:
                break
    zipf.close()
    response = HttpResponse(stream.getvalue())
    response['content_type'] = 'application/zip'
    response['Content-Disposition'] = 'attachement;filename={}'.format(
        _title_to_filename(json_config_dat['title']))
    stream.close()
    return response


def delete(request):
    """Delete experiment data"""
    location = json.load(request)['location']
    try:
        os.remove(os.path.join(
            settings.MEDIA_ROOT, "experiments", location, 'config.json'))
    except FileNotFoundError:
        pass
    try:
        os.remove(os.path.join(
            settings.MEDIA_ROOT, "experiments", location, 'data.npy'))
    except FileNotFoundError:
        for i in range(1000):
            try:
                os.remove(os.path.join(
                    settings.MEDIA_ROOT, "experiments", location, 'data_{:03d}.npy'.format(i)))
            except FileNotFoundError:
                break
    try:
        os.rmdir(os.path.join(
            settings.MEDIA_ROOT, "experiments", location))
    except FileNotFoundError:
        pass
    return status(request)


def progress_plots(request, path):
    """Get a PNG plot"""
    print('request for {}'.format(os.path.join(
        settings.MEDIA_ROOT, 'figures/progress_plot', path)))
    serve(request, 'figures/progress_plot/' + path,
          document_root=settings.MEDIA_ROOT)


def _title_to_filename(title):
    """convert title to a filename"""
    filename = ''.join(
        ['_' if c in '_.- ' else c
         for c in list(title)
         if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.- "][:25])
    if filename == '':
        return 'data.zip'
    return filename + '.zip'
