# backend/core/views.py

from django.http import JsonResponse

def generate_timetable_view(request):
    # In Phase 2, the actual AI logic will go here.
    # For now, we just confirm the API is working.

    print("API was called! Triggering timetable generation...")

    return JsonResponse({
        'status': 'success',
        'message': 'Timetable generation process has been started!'
    })
