"""
URL configuration for backend_cafeteria project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path


def root_login_redirect(request):
    return redirect('/admin/login/?next=/admin/')

urlpatterns = [
    path('', root_login_redirect),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/usuarios/', include('usuarios.urls')),
    path('api/empleados/', include('empleados.urls')),
    path('api/productos/', include('productos.urls')),
    path('api/ventas/', include('ventas.urls')),
]
