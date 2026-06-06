from django.conf import settings
from django.db import models


class CategoriaProducto(models.Model):
	descripcion = models.CharField(max_length=100, unique=True)

	def __str__(self):
		return self.descripcion


class Producto(models.Model):
	nombre = models.CharField(max_length=150)
	codigo = models.CharField(max_length=50, unique=True, null=True, blank=True)
	categoria = models.ForeignKey(
		CategoriaProducto,
		on_delete=models.PROTECT,
		related_name='productos',
	)
	precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
	stock = models.PositiveIntegerField(default=0)
	estado = models.BooleanField(default=True)

	class Meta:
		ordering = ['nombre']

	def __str__(self):
		return self.nombre


class MovimientoInventario(models.Model):
	TIPO_ENTRADA = 'ENTRADA'
	TIPO_SALIDA = 'SALIDA'
	TIPO_AJUSTE = 'AJUSTE'
	TIPO_CHOICES = [
		(TIPO_ENTRADA, 'Entrada'),
		(TIPO_SALIDA, 'Salida'),
		(TIPO_AJUSTE, 'Ajuste'),
	]

	producto = models.ForeignKey(
		Producto,
		on_delete=models.PROTECT,
		related_name='movimientos_inventario',
	)
	tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
	cantidad = models.PositiveIntegerField()
	stock_anterior = models.PositiveIntegerField()
	stock_nuevo = models.PositiveIntegerField()
	descripcion = models.CharField(max_length=255, blank=True)
	usuario = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='movimientos_inventario',
	)
	fecha = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-fecha', '-id']

	def __str__(self):
		return f'{self.producto} - {self.tipo} - {self.cantidad}'
