"""openinfradays URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('sessions', views.session_list),
    path('session/<int:session_id>', views.session_detail),
    path('about', views.about),
    path('registration_check', views.registration_check),
    path('schedule_day1', views.schedules_day1),
    path('schedule_day2', views.schedules_day2),
    path('schedule/day1', views.schedules_day1),
    path('schedule/day2', views.schedules_day2),
    path('handsonlab', views.handsonlab),
    path('handsonlab/<str:title>', views.handsonlab_detail),
   # path('handsonlab/<str:handsonlab_title>/apply/<str:option>', views.handsonlab_apply),
    #path('handsonlab/<str:handsonlab_title>/apply', views.handsonlab_apply),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "openinfradays.views.handler404"
