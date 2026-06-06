from django.db import models

from empleados.models import Empleado
from productos.models import Producto


class Cliente(models.Model):
	nombre = models.CharField(max_length=150)
	ci_nit = models.CharField(max_length=25, unique=True)
	fecha_nacimiento = models.DateField(null=True, blank=True)
	celular = models.CharField(max_length=20, blank=True)
	email = models.EmailField(blank=True)
	direccion = models.CharField(max_length=255, blank=True)

	def __str__(self):
		return self.nombre


class NotaVenta(models.Model):
	empleado = models.ForeignKey(
		Empleado,
		on_delete=models.CASCADE,
		related_name='notas_venta',
	)
	cliente = models.ForeignKey(
		Cliente,
		on_delete=models.CASCADE,
		related_name='notas_venta',
	)
	fecha = models.DateTimeField(auto_now_add=True)
	observacion = models.TextField(blank=True)
	total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

	class Meta:
		ordering = ['-fecha', '-id']

	def __str__(self):
		return f'Nota {self.id}'


class DetalleVenta(models.Model):
	nota_venta = models.ForeignKey(
		NotaVenta,
		on_delete=models.CASCADE,
		related_name='detalles',
	)
	producto = models.ForeignKey(
		Producto,
		on_delete=models.CASCADE,
		related_name='detalles_venta',
	)
	cantidad = models.PositiveIntegerField()
	descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
	subtotal = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self):
		return f'{self.producto} x {self.cantidad}'
