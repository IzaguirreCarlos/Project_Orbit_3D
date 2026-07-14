"""
ProjectForge 3D — URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# ─── API v1 ───────────────────────────────────────────────────
api_v1_patterns = [
    path('auth/', include('apps.accounts.urls')),
    path('projects/', include('apps.projects.urls')),
    path('tasks/', include('apps.tasks.urls')),
    path('messaging/', include('apps.messaging.urls')),
    path('analytics/', include('apps.analytics.urls')),
]

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API REST
    path('api/v1/', include(api_v1_patterns)),

    # API Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Health check (Render probe)
    path('api/health/', include('apps.core.health_urls')),

    # Frontend Views
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.web_urls')),
    path('projects/', include('apps.projects.web_urls')),
]

# ─── Dev: servir media y debug toolbar ────────────────────────
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    try:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
