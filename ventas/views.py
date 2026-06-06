from datetime import datetime, timedelta
from decimal import Decimal

from django.db.models import Sum, Count, Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from backend_cafeteria.permissions import IsStaffOnly
from productos.models import MovimientoInventario

from .models import Cliente, DetalleVenta, NotaVenta
from .serializers import ClienteSerializer, DetalleVentaSerializer, NotaVentaSerializer, ReporteVentasSerializer


class ClienteViewSet(viewsets.ModelViewSet):
	queryset = Cliente.objects.all().order_by('id')
	serializer_class = ClienteSerializer


class NotaVentaViewSet(viewsets.ModelViewSet):
	queryset = NotaVenta.objects.all().select_related('cliente', 'empleado')
	serializer_class = NotaVentaSerializer

	def perform_create(self, serializer):
		empleado = getattr(self.request.user, 'empleado', None)
		if empleado is None:
			raise ValidationError({'empleado': 'El usuario autenticado no tiene un empleado asociado.'})
		serializer.save(empleado=empleado)


class DetalleVentaViewSet(viewsets.ModelViewSet):
	queryset = DetalleVenta.objects.all().select_related('nota_venta', 'producto')
	serializer_class = DetalleVentaSerializer

	def perform_destroy(self, instance):
		producto = instance.producto
		stock_anterior = producto.stock
		stock_nuevo = producto.stock + instance.cantidad
		producto.stock = stock_nuevo
		producto.save(update_fields=['stock'])
		request = self.request
		MovimientoInventario.objects.create(
			producto=producto,
			tipo=MovimientoInventario.TIPO_ENTRADA,
			cantidad=instance.cantidad,
			stock_anterior=stock_anterior,
			stock_nuevo=stock_nuevo,
			usuario=request.user if request and request.user.is_authenticated else None,
			descripcion=f'Retorno por eliminación de detalle de venta #{instance.nota_venta.id}',
		)
		nota_venta = instance.nota_venta
		instance.delete()
		nota_venta.total = sum((item.subtotal for item in nota_venta.detalles.all()), 0)
		nota_venta.save(update_fields=['total'])


class ReporteVentasView(APIView):
	permission_classes = [IsStaffOnly]

	"""
	Vista para generar reportes de ventas con filtros opcionales de fecha.
	
	Parámetros query:
	- fecha_inicio: (opcional) Fecha inicial en formato YYYY-MM-DD
	- fecha_fin: (opcional) Fecha final en formato YYYY-MM-DD
	"""
	
	def get(self, request):
		try:
			# Obtener parámetros de fecha
			fecha_inicio = request.query_params.get('fecha_inicio')
			fecha_fin = request.query_params.get('fecha_fin')
			
			# Construir filtros
			filtro_fecha = Q()
			if fecha_inicio:
				try:
					fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
					filtro_fecha &= Q(fecha__date__gte=fecha_inicio_obj)
				except ValueError:
					return Response(
						{'error': 'Formato de fecha_inicio inválido. Use YYYY-MM-DD'},
						status=status.HTTP_400_BAD_REQUEST
					)
			
			if fecha_fin:
				try:
					fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
					# Incluir todo el día final
					fecha_fin_obj += timedelta(days=1)
					filtro_fecha &= Q(fecha__date__lt=fecha_fin_obj)
				except ValueError:
					return Response(
						{'error': 'Formato de fecha_fin inválido. Use YYYY-MM-DD'},
						status=status.HTTP_400_BAD_REQUEST
					)
			
			# 1. Total general de ventas
			total_ventas = NotaVenta.objects.filter(filtro_fecha).aggregate(
				total=Sum('total')
			)['total'] or Decimal('0.00')
			
			# 2. Cantidad de notas de venta
			cantidad_notas = NotaVenta.objects.filter(filtro_fecha).count()
			
			# 3. Ventas agrupadas por día
			ventas_por_dia_qs = NotaVenta.objects.filter(filtro_fecha).extra(
				select={'fecha_solo': 'DATE(fecha)'}
			).values('fecha_solo').annotate(
				total=Sum('total'),
				cantidad=Count('id')
			).order_by('fecha_solo')
			
			ventas_por_dia = [
				{
					'fecha': str(item['fecha_solo']),
					'total': float(item['total'] or 0),
					'cantidad': item['cantidad']
				}
				for item in ventas_por_dia_qs
			]
			
			# 4. Producto más vendido
			producto_mas_vendido_qs = DetalleVenta.objects.filter(
				nota_venta__in=NotaVenta.objects.filter(filtro_fecha)
			).values('producto__id', 'producto__nombre').annotate(
				cantidad_total=Sum('cantidad'),
				monto_total=Sum('subtotal')
			).order_by('-cantidad_total').first()
			
			producto_mas_vendido = {}
			if producto_mas_vendido_qs:
				producto_mas_vendido = {
					'id': producto_mas_vendido_qs['producto__id'],
					'nombre': producto_mas_vendido_qs['producto__nombre'],
					'cantidad_vendida': int(producto_mas_vendido_qs['cantidad_total']),
					'monto_vendido': float(producto_mas_vendido_qs['monto_total'] or 0)
				}
			
			# 5. Top 5 clientes por monto comprado
			top_clientes_qs = NotaVenta.objects.filter(filtro_fecha).values(
				'cliente__id', 'cliente__nombre'
			).annotate(
				total_comprado=Sum('total'),
				cantidad_compras=Count('id')
			).order_by('-total_comprado')[:5]
			
			top_clientes = [
				{
					'id': item['cliente__id'],
					'nombre': item['cliente__nombre'],
					'total_comprado': float(item['total_comprado'] or 0),
					'cantidad_compras': item['cantidad_compras']
				}
				for item in top_clientes_qs
			]

			# 6. Top 5 empleados por notas emitidas y total vendido
			top_empleados_qs = NotaVenta.objects.filter(filtro_fecha).values(
				'empleado__id', 'empleado__nombre'
			).annotate(
				cantidad_notas=Count('id'),
				total_vendido=Sum('total')
			).order_by('-cantidad_notas', '-total_vendido', 'empleado__nombre')[:5]

			top_empleados = [
				{
					'id': item['empleado__id'],
					'nombre': item['empleado__nombre'],
					'cantidad_notas': item['cantidad_notas'],
					'total_vendido': float(item['total_vendido'] or 0),
				}
				for item in top_empleados_qs
			]
			
			# Preparar datos para serializar
			datos_reporte = {
				'total_ventas': total_ventas,
				'cantidad_notas': cantidad_notas,
				'ventas_por_dia': ventas_por_dia,
				'producto_mas_vendido': producto_mas_vendido,
				'top_clientes': top_clientes,
				'top_empleados': top_empleados
			}
			
			# Serializar
			serializer = ReporteVentasSerializer(datos_reporte)
			return Response(serializer.data, status=status.HTTP_200_OK)
			
		except Exception as e:
			return Response(
				{'error': str(e)},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)
