import os.path
from django.shortcuts import render

def index(request):
    context = {"version": "0.7.0", "plugins": [
        {"type": "instrument",
         "elm_module": "PLACEDemo",
         "python_module": "place_demo",
         "description": "PLACE Demo",
        },
        ],
              }
    return render(request, 'web/place.html', context)
