# core/admin.py

from django.contrib import admin
from .models import Faculty, Room, Course, StudentGroup

# Register your models here.
admin.site.register(Faculty)
admin.site.register(Room)
admin.site.register(Course)
admin.site.register(StudentGroup)