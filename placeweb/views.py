"""Django views for PLACE"""
import io
import os.path
import json
import time
import zipfile
import glob

import pkg_resources
from django.conf import settings
from django.http import HttpResponse, JsonResponse, Http404
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
    """Attempt to start a new experiment"""
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
    current = worker.status()
    if current['status'] == worker.READY:
        current['history'] = history()
    return JsonResponse(current)


def abort(request):
    """Abort a PLACE experiment"""
    worker.abort()
    return status(request)


def history():
    """Get summary of experiments stored on the server"""
    version = pkg_resources.require("place")[0].version
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
            try:
                experiment_entry['version'] = config['metadata']['PLACE_version']
            except KeyError:
                experiment_entry['version'] = "0.0.0"
            try:
                experiment_entry['timestamp'] = config['metadata']['timestamp']
            except KeyError:
                experiment_entry['timestamp'] = 0
            try:
                experiment_entry['title'] = config['title']
            except KeyError:
                experiment_entry['title'] = "untitled"
            try:
                experiment_entry['comments'] = config['comments']
            except KeyError:
                experiment_entry['comments'] = "no comments"
            experiment_entry['location'] = item
            experiment_entry['filename'] = _title_to_filename(
                experiment_entry['title'])
            experiment_entries.append(experiment_entry)
        except FileNotFoundError:
            experiment_entry = {}
            experiment_entry['version'] = "0.0.0"
            experiment_entry['timestamp'] = 0
            experiment_entry['title'] = "<invalid>"
            experiment_entry['comments'] = "<missing config.json>"
            experiment_entry['location'] = item
            experiment_entry['filename'] = "data.zip"
            experiment_entries.append(experiment_entry)
        except KeyError as err:
            print('Experiment in {} is missing config values: {}'.format(
                os.path.join(path, item), err))
            experiment_entry = {}
            experiment_entry['version'] = version
            experiment_entry['timestamp'] = 0
            experiment_entry['title'] = "<invalid>"
            experiment_entry['comments'] = "<missing values in config.json>"
            experiment_entry['location'] = item
            experiment_entry['filename'] = "data.zip"
            experiment_entries.append(experiment_entry)
    return {'experiment_entries': sorted(experiment_entries, key=timestamp_to_millis, reverse=True)}


def timestamp_to_millis(entry):
    """Convert timestamps to milliseconds (if not already)"""
    if isinstance(entry['timestamp'], int):
        return entry['timestamp']
    # The following code is really only needed for
    # experiments created with PLACE prior to version 0.8
    return time.mktime(time.strptime(entry['timestamp'], r'%Y-%m-%d %H:%M:%S.%f'))


def results(request):  # pylint: disable=unused-argument
    """Return the final results from an experiment"""
    location = json.load(request)['location']
    res = os.path.join(settings.MEDIA_ROOT, "experiments",
                       location, 'results.json')
    con = os.path.join(settings.MEDIA_ROOT, "experiments",
                       location, 'config.json')
    try:
        # if there is a results file, then it must have completed
        with open(res) as file_p:
            json_results_dat = json.load(file_p)
        return JsonResponse(
            {
                "result": "completed",
                "progress": json_results_dat
            }
        )
    except FileNotFoundError:
        try:
            # no results file means it was aborted or had an error but we can
            # still send the config data back to repeat the experiment
            with open(con) as file_p:
                json_experiment_dat = json.load(file_p)
            return JsonResponse(
                {
                    "result": "aborted",
                    "experiment": json_experiment_dat
                }
            )
        except FileNotFoundError:
            pass
    # there is nothing useful to report
    return JsonResponse(
        {
            "result": "empty",
            "location": os.path.dirname(res)
        }
    )


def download(request, location):  # pylint: disable=unused-argument
    """Download experiment data"""
    path = os.path.join(settings.MEDIA_ROOT, "experiments", location)
    stream = io.BytesIO()
    zipf = zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED)
    try:
        with open(os.path.join(path, 'config.json')) as file_p:
            json_config_dat = json.load(file_p)
        zipf.write(os.path.join(path, 'config.json'), arcname='config.json')
        title = json_config_dat['title']
    except FileNotFoundError:
        raise Http404('Missing PLACE experiment data')
    try:
        zipf.write(os.path.join(path, 'results.json'), arcname='results.json')
    except FileNotFoundError:
        title = 'incomplete_' + title
    try:
        zipf.write(os.path.join(path, 'data.npy'), arcname='data.npy')
    except FileNotFoundError:
        for filename in glob.glob(path + '/data_*.npy'):
            zipf.write(filename, arcname=os.path.basename(filename))
    for filename in glob.glob(path + '/*.png'):
        zipf.write(filename, arcname=os.path.basename(filename))
    for filename in glob.glob(path + '/*.csv'):
        zipf.write(filename, arcname=os.path.basename(filename))
    zipf.close()
    response = HttpResponse(stream.getvalue())
    response['content_type'] = 'application/zip'
    response['Content-Disposition'] = 'attachement;filename={}'.format(
        _title_to_filename(title))
    stream.close()
    return response


def delete(request):
    """Delete experiment data"""
    location = os.path.join(
        settings.MEDIA_ROOT,
        "experiments",
        json.load(request)['location']
    )
    try:
        os.remove(os.path.join(location, 'config.json'))
    except FileNotFoundError:
        pass
    try:
        os.remove(os.path.join(location, 'results.json'))
    except FileNotFoundError:
        pass
    try:
        os.remove(os.path.join(location, 'data.npy'))
    except FileNotFoundError:
        for filename in glob.glob(location + '/data*.npy'):
            os.remove(filename)
    for filename in glob.glob(location + '/*.png'):
        os.remove(filename)
    try:
        os.rmdir(location)
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
        ['_' if c in '_. ' else c
         for c in list(title)
         if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.- "][:100])
    if filename == '':
        return 'data.zip'
    return filename + '.zip'
