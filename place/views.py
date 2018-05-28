"""The PLACE web views"""
from django.http import HttpResponse

def index(request):
    return HttpResponse('This is the place web app')
