from django.urls import path
from .views import compare_view

urlpatterns = [
    path('compare/', compare_view, name='compare'),
]