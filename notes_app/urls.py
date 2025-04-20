"""
URL configuration for notes_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
# project_name/urls.py
from django.contrib import admin
from django.urls import path, include  # Import include to include the core app's URLs
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin page
    path('', include('core.urls')),  # Include the URLs from the core app (main URL pattern)
    path('QnA_forum/', include('QnA_forum.urls')),  # ✅ This connects the Q&A Forum
    path('notes_feature/',include('notes_feature.urls')),
    path('accounts/profile/', RedirectView.as_view(url='/profile/', permanent=False)),
]


# ✅ Serve uploaded images in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
