from django.urls import path
from .views import predict_intentions

urlpatterns = [
    path('predict_intentions/', predict_intentions, name='predict_intentions'),
]
