from rest_framework import viewsets

from backend_cafeteria.permissions import IsStaffOrReadOnly

from .models import Empleado, EstadoCivil, Nacionalidad, Salario, TipoContrato, Turno
from .serializers import (
	EmpleadoSerializer,
	EstadoCivilSerializer,
	NacionalidadSerializer,
	SalarioSerializer,
	TipoContratoSerializer,
	TurnoSerializer,
)


class EstadoCivilViewSet(viewsets.ModelViewSet):
	queryset = EstadoCivil.objects.all().order_by('id')
	serializer_class = EstadoCivilSerializer
	permission_classes = [IsStaffOrReadOnly]


class NacionalidadViewSet(viewsets.ModelViewSet):
	queryset = Nacionalidad.objects.all().order_by('id')
	serializer_class = NacionalidadSerializer
	permission_classes = [IsStaffOrReadOnly]


class TurnoViewSet(viewsets.ModelViewSet):
	queryset = Turno.objects.all().order_by('id')
	serializer_class = TurnoSerializer
	permission_classes = [IsStaffOrReadOnly]


class TipoContratoViewSet(viewsets.ModelViewSet):
	queryset = TipoContrato.objects.all().order_by('id')
	serializer_class = TipoContratoSerializer
	permission_classes = [IsStaffOrReadOnly]


class EmpleadoViewSet(viewsets.ModelViewSet):
	queryset = Empleado.objects.all().select_related(
		'user',
		'estado_civil',
		'nacionalidad',
		'turno',
		'tipo_contrato',
	)
	serializer_class = EmpleadoSerializer
	permission_classes = [IsStaffOrReadOnly]


class SalarioViewSet(viewsets.ModelViewSet):
	queryset = Salario.objects.all().select_related('empleado')
	serializer_class = SalarioSerializer
	permission_classes = [IsStaffOrReadOnly]
