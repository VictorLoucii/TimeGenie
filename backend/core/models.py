# backend/core/models.py

from django.db import models

# 1. Course MUST be defined first so Faculty can refer to it
class Course(models.Model):
    COURSE_TYPES = [
        ('THEORY', 'Theory'),
        ('LAB', 'Practical/Lab'),
    ]
    name = models.CharField(max_length=100)
    course_type = models.CharField(max_length=10, choices=COURSE_TYPES)
    
    def __str__(self):
        return f"{self.name} ({self.get_course_type_display()})"

# 2. Faculty now links to ONE Course
class Faculty(models.Model):
    name = models.CharField(max_length=100)
    # ForeignKey = Only 1 Subject per Teacher
    subject = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='instructors') 
    
    def __str__(self):
        return self.name

class Room(models.Model):
    ROOM_TYPES = [
        ('THEORY', 'Theory Hall'),
        ('LAB', 'Computer Lab'),
    ]
    name = models.CharField(max_length=50)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
    
    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"

class StudentGroup(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name