from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ClienteViewSet, DetalleVentaViewSet, NotaVentaViewSet, ReporteVentasView

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='clientes')
router.register(r'notas-venta', NotaVentaViewSet, basename='notas-venta')
router.register(r'detalles-venta', DetalleVentaViewSet, basename='detalles-venta')

urlpatterns = [
    path('', include(router.urls)),
    path('reporte/', ReporteVentasView.as_view(), name='reporte-ventas'),
]