"""The PLACE database model"""
from django.db import models

def make_upload(instance, _):
    """Create an upload directory for the experiment"""
    return 'experiments/{}/'.format(instance.experiment_id)

# Create your models here.
class Experiment(models.Model):
    """A model describing a PLACE experiment"""
    experiment_id = models.AutoField(primary_key=True)
    submitted = models.DateTimeField(auto_now_add=True)
    config = models.FileField(upload_to=make_upload)
    metadata = models.FileField(upload_to=make_upload)
    data = models.FileField(upload_to=make_upload)
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
