from django.conf import settings
from django.db import models


class Estado(models.Model):
	usuario = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='estado',
	)
	activo = models.BooleanField(default=True)

	def __str__(self):
		estado_str = 'Activo' if self.activo else 'Inactivo'
		return f'{self.usuario.username} - {estado_str}'


class Bitacora(models.Model):
	usuario = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='bitacoras',
	)
	accion = models.CharField(max_length=120)
	detalle = models.TextField(blank=True)
	fecha = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-fecha']

	def __str__(self):
		return f'{self.usuario} - {self.accion}'
