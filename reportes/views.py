# reportes/views.py
"""Vistas de la app reportes — W02 (placeholder)."""
from django.shortcuts import render
import hmac
import os

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


def index(request):
    """Vista de índice de reportes."""
    context = {
        'titulo': 'Reportes',
        'descripcion': 'Dashboard, KPIs y exportación de datos.',
        'espiral': 'Espiral 7 · W19',
    }
    return render(request, 'reportes/index.html', context)
