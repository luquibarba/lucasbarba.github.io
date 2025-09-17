# personal_blog/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),  # Todas las rutas del blog van con prefijo /blog/
    path('', include('blog.urls')),       # También permitir acceso directo desde la raíz
]

# Servir archivos media durante el desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)