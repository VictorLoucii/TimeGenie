# backend/core/urls.py

from django.urls import path
from .views import generate_timetable_view

urlpatterns = [
    path('generate/', generate_timetable_view, name='generate-timetable'),
]