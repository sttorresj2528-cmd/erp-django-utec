import hmac
import os

from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from ventas.tasks import verificar_stock_bajo, reporte_ventas_diario

TAREAS = {
    'stock-bajo': verificar_stock_bajo,
    'reporte-diario': reporte_ventas_diario,
}


def _autorizado(request):
    token = os.environ.get('CRON_TOKEN', '')
    recibido = request.headers.get('Authorization', '').removeprefix('Bearer ').strip()
    return bool(token) and hmac.compare_digest(token, recibido)


def health(request):
    return JsonResponse({'ok': True})


@csrf_exempt
def ejecutar(request, nombre):
    if not _autorizado(request):
        return HttpResponseForbidden('No autorizado')
    tarea = TAREAS.get(nombre)
    if tarea is None:
        return JsonResponse({'error': 'tarea no existe'}, status=404)
    resultado = tarea.apply().get()   # corre directo, sin Redis ni worker
    return JsonResponse({'tarea': nombre, 'resultado': str(resultado)})