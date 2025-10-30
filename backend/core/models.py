# core/models.py

from django.db import models

class Faculty(models.Model):
    name = models.CharField(max_length=100)
    
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

class Course(models.Model):
    COURSE_TYPES = [
        ('THEORY', 'Theory'),
        ('LAB', 'Practical/Lab'),
    ]
    name = models.CharField(max_length=100)
    course_type = models.CharField(max_length=10, choices=COURSE_TYPES)
    
    def __str__(self):
        return f"{self.name} ({self.get_course_type_display()})"

class StudentGroup(models.Model):
    name = models.CharField(max_length=100) # e.g., "Full Class", "G1", "G2"
    
    def __str__(self):
        return self.name

#note: The __str__ method in each class is important—it tells Django to use the object's name (like "Dr. Smith") in the admin interface, which is much more readable than "Faculty object (1)".

# We will define TimeSlot later if needed, for now the AI can generate them.
# The final Timetable model will be built in a later phase.