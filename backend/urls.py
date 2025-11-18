from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('letterboxd_scraper/', include('letterboxd_scraper.urls')),
]
