"""VA_Project_Mapid URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from authorship_attribution import views as v

urlpatterns = [
    url(r'^$', v.index, name='index'),
    url(r'^author/fetchdata/$', v.live_processing, name='live_processing'),
    url(r'^author/make_clusters/$', v.make_force, name='make_force'),
    url(r'^author/make_bar/$', v.make_bars, name='make_bars'),
    url(r'^admin/', admin.site.urls),
]
