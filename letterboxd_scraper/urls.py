from django.urls import path
from .views import home_view, compare_view

urlpatterns = [
    path('compare/', compare_view, name='compare'),
    path('', home_view, name='home'),
]