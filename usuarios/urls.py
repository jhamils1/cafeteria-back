from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BitacoraViewSet, PermissionViewSet, RoleViewSet, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'groupsAux', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'bitacoras', BitacoraViewSet, basename='bitacoras')

urlpatterns = [
    path('', include(router.urls)),
]