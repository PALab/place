"""Admin controls for the Django SQLite database"""
from django.contrib import admin

# Register your models here.
from .models import Experiment

admin.site.register(Experiment)
