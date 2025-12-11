# backend/core/views.py

from django.http import JsonResponse
from .ga import TimetableGA # Import our new AI Class

def generate_timetable_view(request):
    try:
        # 1. Initialize the AI Engine
        ga_engine = TimetableGA()
        
        # 2. Check if we actually have data to process
        if ga_engine.num_genes == 0:
             return JsonResponse({
                'status': 'error', 
                'message': 'No courses or student groups found in database! Add some via Admin panel.'
            })

        # 3. Run the Algorithm
        timetable = ga_engine.run()

        # 4. Return the results
        return JsonResponse({
            'status': 'success',
            'fitness_score': 'Optimized',
            'data': timetable
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
