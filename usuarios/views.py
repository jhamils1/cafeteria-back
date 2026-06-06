from django.contrib.auth.models import Group, Permission, User
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend_cafeteria.permissions import IsStaffOnly

from .models import Bitacora
from .serializers import (
	BitacoraSerializer,
	CurrentUserSerializer,
	PermissionSerializer,
	RoleSerializer,
	UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all().select_related('estado').prefetch_related('groups').order_by('id')
	serializer_class = UserSerializer
	permission_classes = [IsStaffOnly]

	@action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
	def me(self, request):
		user = (
			User.objects.select_related('estado')
			.prefetch_related('groups__permissions', 'groups')
			.get(pk=request.user.pk)
		)
		serializer = CurrentUserSerializer(user, context={'request': request})
		return Response(serializer.data)


class BitacoraViewSet(viewsets.ModelViewSet):
	queryset = Bitacora.objects.all().select_related('usuario')
	serializer_class = BitacoraSerializer
	permission_classes = [IsStaffOnly]


class RoleViewSet(viewsets.ModelViewSet):
	queryset = Group.objects.all().order_by('name')
	serializer_class = RoleSerializer
	permission_classes = [IsStaffOnly]


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Permission.objects.all().order_by('content_type__app_label', 'codename')
	serializer_class = PermissionSerializer
	permission_classes = [IsStaffOnly]
