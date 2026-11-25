from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@staff_member_required
@require_http_methods(['GET', 'POST'])
def enviar_reporte_ahora(request):
    """Muestra un botón y, al pulsarlo, envía el reporte de ventas del día."""
    destino = settings.ADMINS[0][1] if settings.ADMINS else None
    contexto = {'destino': destino, 'resultado': None, 'error': None}

    if request.method == 'POST':
        if not destino:
            contexto['error'] = (
                'No hay correo de administrador configurado '
                '(ADMINS / ADMIN_EMAIL en Render).'
            )
        else:
            try:
                from ventas.tasks import reporte_ventas_diario
                contexto['resultado'] = reporte_ventas_diario()
            except Exception as exc:
                contexto['error'] = f'No se pudo enviar el reporte: {exc}'

    return render(request, 'reporte_enviar.html', contexto)