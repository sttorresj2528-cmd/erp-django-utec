import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

UMBRAL_STOCK = 5   # mismo umbral por defecto que verificar_stock_bajo (W17)


def _enviar(asunto, texto, html, destinos):
    """Envía un correo texto+HTML. Nunca rompe la venta si falla."""
    try:
        msg = EmailMultiAlternatives(
            subject=asunto,
            body=texto,
           from_email=settings.DEFAULT_FROM_EMAIL,
            to=destinos,
        )
        msg.attach_alternative(html, 'text/html')
        msg.send()
        return True
    except Exception:
        logger.exception('No se pudo enviar el correo: %s', asunto)
        return False


def _correo_admin():
    admins = getattr(settings, 'ADMINS', [])
    return admins[0][1] if admins else None


def _estado_stock(stock):
    if stock <= 0:
        return 'AGOTADO', '#ff0033'
    if stock < UMBRAL_STOCK:
        return 'BAJO', '#ffb800'
    return 'OK', '#22c55e'


# ── 1. Ticket al cliente ─────────────────────────────────────────────
def enviar_ticket_venta(venta):
    correo = getattr(venta.cliente, 'correo', None)
    if not correo:
        return False
    detalles = venta.detalles.select_related('producto')
    html = render_to_string('emails/ticket_venta.html',
                            {'venta': venta, 'detalles': detalles})
    texto = f'Gracias por tu compra. Venta #{venta.pk}. Total: ${venta.total:.2f}'
    return _enviar(f'Ticket de compra #{venta.pk}', texto, html, [correo])


# ── 2. Producto vendido (al admin) ───────────────────────────────────
def enviar_aviso_producto_vendido(venta):
    admin = _correo_admin()
    if not admin:
        return False
    detalles = venta.detalles.select_related('producto')
    html = render_to_string('emails/producto_vendido.html',
                            {'venta': venta, 'detalles': detalles})
    lineas = '\n'.join(
        f'- {d.producto.nombre} x{d.cantidad} = ${d.subtotal:.2f}' for d in detalles
    )
    texto = (f'Venta #{venta.pk} a {venta.cliente}\n{lineas}\n'
             f'TOTAL: ${venta.total:.2f}')
    return _enviar(f'Producto vendido: venta #{venta.pk}', texto, html, [admin])


# ── 3. Stock tras la venta (al admin) ────────────────────────────────
def enviar_aviso_stock(venta):
    admin = _correo_admin()
    if not admin:
        return False
    filas = []
    for d in venta.detalles.select_related('producto'):
        estado, color = _estado_stock(d.producto.stock)
        filas.append({
            'nombre':  d.producto.nombre,
            'vendidas': d.cantidad,
            'stock':   d.producto.stock,
            'estado':  estado,
            'color':   color,
        })
    html = render_to_string('emails/stock_venta.html',
                            {'venta': venta, 'filas': filas, 'umbral': UMBRAL_STOCK})
    texto = f'Stock tras la venta #{venta.pk}\n' + '\n'.join(
        f"- {f['nombre']}: quedan {f['stock']} ({f['estado']})" for f in filas
    )
    return _enviar(f'Stock tras la venta #{venta.pk}', texto, html, [admin])


# ── Dispara los 3 ────────────────────────────────────────────────────
def enviar_correos_venta(venta):
    enviar_ticket_venta(venta)
    enviar_aviso_producto_vendido(venta)
    enviar_aviso_stock(venta)