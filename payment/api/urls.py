from django.urls import path

from payment.api import views

urlpatterns = [
    path('response', views.response_view),
    path('request', views.request_view),
]
