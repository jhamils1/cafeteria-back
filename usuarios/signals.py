from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Estado


@receiver(post_save, sender=User)
def crear_estado_usuario(sender, instance, created, **kwargs):
	if not created:
		return

	Estado.objects.get_or_create(usuario=instance, defaults={'activo': True})
