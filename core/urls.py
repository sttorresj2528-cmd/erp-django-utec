# core/urls.py — agregar las rutas de API y token
from core.reporte_views import enviar_reporte_ahora
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from . import views

# Importar y combinar todas las URLs de la API
from productos.api_urls   import urlpatterns as productos_api
from clientes.api_urls    import urlpatterns as clientes_api
from proveedores.api_urls import urlpatterns as proveedores_api
from ventas.api_urls      import urlpatterns as ventas_api

from core.reporte_views import enviar_reporte_ahora, disparar_reporte

api_urlpatterns = (
    productos_api +
    clientes_api  +
    proveedores_api +
    ventas_api
)

# core/urls.py — agregar la ruta del catálogo:
urlpatterns = [    
    path('cron/reporte/', disparar_reporte, name='cron_reporte'),
    path('reporte/enviar/', enviar_reporte_ahora, name='reporte_enviar'),
    path('admin/',      admin.site.urls),
    path('',            views.bienvenida,             name='inicio'),
    path('accounts/',   include('allauth.urls')),
    # API REST
    path('api/',        include((api_urlpatterns, 'api'))),
    path('api/auth/token/', obtain_auth_token, name='api_token'),
    # E-commerce público — W13
    path('catalogo/',   include('catalogo.urls', namespace='catalogo')),
    # Apps del ERP (interfaz interna)
    path('clientes/',    include('clientes.urls',    namespace='clientes')),
    path('proveedores/', include('proveedores.urls', namespace='proveedores')),
    path('productos/',   include('productos.urls',   namespace='productos')),
    path('ventas/',      include('ventas.urls',       namespace='ventas')),
    path('reportes/',    include('reportes.urls',     namespace='reportes')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)