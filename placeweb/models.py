"""The PLACE database model"""
from django.db import models


def make_config(instance, _):
    """Create the config file path for the experiment"""
    return 'experiments/{:06d}/config.json'.format(instance.experiment_id)


def make_metadata(instance, _):
    """Create the metadata file path for the experiment"""
    return 'experiments/{:06d}/metadata.json'.format(instance.experiment_id)


def make_data(instance, _):
    """Create the data file path for the experiment"""
    return 'experiments/{:06d}/data.npy'.format(instance.experiment_id)

# Create your models here.


class Experiment(models.Model):
    """A model describing a PLACE experiment"""
    experiment_id = models.AutoField(primary_key=True)
    submitted = models.DateTimeField(auto_now_add=True)
    config = models.FileField(upload_to=make_config)
    metadata = models.FileField(upload_to=make_metadata)
    data = models.FileField(upload_to=make_data)
    queued = 'Q'
    running = 'R'
    finished = 'F'
    status_choices = (
        (queued, 'Queued'),
        (running, 'Running'),
        (finished, 'Finished')
    )
    status = models.CharField(
        max_length=1,
        choices=status_choices,
        default=queued
    )
