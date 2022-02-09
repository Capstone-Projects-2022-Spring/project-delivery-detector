from django.urls import include, path
from django.contrib import admin
from rest_framework import routers
from .quick_api import views

# Create a default router object for the API endpoints 
router = routers.DefaultRouter()
router.register(r'helloworld', views.HelloWorldSet)
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', views.HelloWorldSet.as_view({'key': 'queryset'})), 
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls)
]