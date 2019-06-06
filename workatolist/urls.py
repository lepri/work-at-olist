from django.conf.urls import url, include
from django.views.generic.base import RedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/api/v1/call/')),
    url(r'^api/', include('call.api.urls')),
]
