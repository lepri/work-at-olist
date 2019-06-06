from django.urls import path
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from call.api import views

router = DefaultRouter()
router.register(r'call', views.CallViewSet)

urlpatterns = [
    path('v1/bill/<str:destination>/', views.BillViewSet.as_view()),
    path('v1/bill/<str:destination>/<int:year>/<int:month>/', views.BillViewSet.as_view()),
    path('v1/', include(router.urls)),
]
