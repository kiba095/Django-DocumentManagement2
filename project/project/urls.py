"""
URL configuration for project project.

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
from django.contrib import admin
from django.urls import path,include
from app.views import notifications,media_detail,index
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

admin.site.site_header = "MOV Submission Repository"
admin.site.site_title = "MOV Portal"
admin.site.index_title = "Welcome to the Portal"

from django.contrib import admin

admin.autodiscover()
admin.site.enable_nav_sidebar = False


urlpatterns = [
    path('admin/',admin.site.urls,name='admin'),
    path('logout/',auth_views.LogoutView.as_view(template_name="registration/logged_out.html"),name='logout'),
    path('notifications/',notifications,name='notifications'),
    path('app/',include('app.urls')),
    path('',index,name ="index")
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)