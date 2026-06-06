from django.conf import settings
from django.db import models


class EstadoCivil(models.Model):
	descripcion = models.CharField(max_length=50, unique=True)

	def __str__(self):
		return self.descripcion


class Nacionalidad(models.Model):
	descripcion = models.CharField(max_length=50, unique=True)

	def __str__(self):
		return self.descripcion


class Turno(models.Model):
	descripcion = models.CharField(max_length=50, unique=True)

	def __str__(self):
		return self.descripcion


class TipoContrato(models.Model):
	descripcion = models.CharField(max_length=80, unique=True)

	def __str__(self):
		return self.descripcion


class Empleado(models.Model):
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='empleado',
	)
	first_name = models.CharField(max_length=120, null=True, blank=True)
	last_name = models.CharField(max_length=120, null=True, blank=True)
	# campo legacy para compatibilidad (se rellenará desde first_name + last_name)
	nombre = models.CharField(max_length=150, blank=True)
	ci = models.CharField(max_length=20, unique=True)
	telefono_fijo = models.CharField(max_length=20, blank=True)
	celular = models.CharField(max_length=20, blank=True)
	telefono_contacto = models.CharField(max_length=20, blank=True)
	email = models.EmailField(blank=True)
	direccion = models.CharField(max_length=255, blank=True)
	nombre_contacto = models.CharField(max_length=150, blank=True)
	estado_civil = models.ForeignKey(
		EstadoCivil,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='empleados',
	)
	nacionalidad = models.ForeignKey(
		Nacionalidad,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='empleados',
	)
	turno = models.ForeignKey(
		Turno,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='empleados',
	)
	tipo_contrato = models.ForeignKey(
		TipoContrato,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='empleados',
	)
	fecha_registro = models.DateTimeField(auto_now_add=True)
	activo = models.BooleanField(default=True)

	def __str__(self):
		return self.nombre


class Salario(models.Model):
	empleado = models.ForeignKey(
		Empleado,
		on_delete=models.CASCADE,
		related_name='salarios',
	)
	descripcion = models.CharField(max_length=120)
	monto = models.DecimalField(max_digits=10, decimal_places=2)
	fecha_inicio = models.DateField()

	class Meta:
		ordering = ['-fecha_inicio', '-id']

	def __str__(self):
		return f'{self.empleado} - {self.monto}'
