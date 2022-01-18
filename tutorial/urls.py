"""tutorial URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include
from rest_framework import routers
from myapp import views
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'persons', views.PersonViewSet)
router.register(r'recommends', views.RecommendView)
router.register(r'hairimgs', views.SimulationStyleListView)
router.register(r'ganrequests', views.GanViewSet)
# router.register(r'coldstarts', views.ColdStartSet)
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('persons/<char:user_id>', views.PersonDetail, name='Person_detail'),
    path('coldstarts/<str:user_id>/', views.coldstart_listup),
    path('coldstarts/<str:user_id>/<str:selected_image>/', views.coldstart_selected),
    path('persontest/<str:user_id>/', views.person_view),
    path('recommend/update/', views.recommend_update),
    path('recommend/', views.recommend_create),
    path('persontest/', views.person_save),
    path('scondata/update/', views.update_data),
    path('scondata/', views.create_data),
    path('scondata/<int:version>/', views.view_data),
    path('admin/', admin.site.urls),
    path('userset/', views.create_userdata)

    #path('recommend/<int:no>/', views.PersonDetail.as_view(), name="recommend_result-detail"),
 ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


