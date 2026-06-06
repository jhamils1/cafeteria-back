from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EmpleadoViewSet,
    EstadoCivilViewSet,
    NacionalidadViewSet,
    SalarioViewSet,
    TipoContratoViewSet,
    TurnoViewSet,
)

router = DefaultRouter()
router.register(r'estados-civiles', EstadoCivilViewSet, basename='estados-civiles')
router.register(r'nacionalidades', NacionalidadViewSet, basename='nacionalidades')
router.register(r'turnos', TurnoViewSet, basename='turnos')
router.register(r'tipos-contrato', TipoContratoViewSet, basename='tipos-contrato')
router.register(r'empleados', EmpleadoViewSet, basename='empleados')
router.register(r'salarios', SalarioViewSet, basename='salarios')

urlpatterns = [
    path('', include(router.urls)),
]