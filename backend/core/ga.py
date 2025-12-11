# TimeGenie/backend/core/ga.py

import pygad
import numpy as np
import random
from collections import defaultdict
from .models import Faculty, Room, Course, StudentGroup

# --- Configuration ---
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
SLOTS_PER_DAY = 8 
TOTAL_SLOTS = len(DAYS) * SLOTS_PER_DAY

class TimetableGA:
    def __init__(self):
        # 1. Fetch Data
        self.rooms = list(Room.objects.all())
        self.instructors = list(Faculty.objects.all())
        self.groups = list(StudentGroup.objects.all())
        self.courses = list(Course.objects.all())
        
        print("\n--- 🕵️‍♂️ GA DEBUGGER ---")
        print(f"Rooms Loaded: {len(self.rooms)}")
        for r in self.rooms:
            print(f"  - Room: {r.name} | Type: '{r.room_type}'")

        # 2. Create "Class Instances"
        self.classes_to_schedule = []
        
        for course in self.courses:
            for group in self.groups:
                g_name = group.name.strip().upper()
                c_type = course.course_type
                
                # Rules
                if c_type == 'LAB' and g_name == 'FULL CLASS': continue
                if c_type == 'THEORY' and g_name in ['G1', 'G2']: continue

                num_sessions = 1 if c_type == 'LAB' else 3
                
                for i in range(num_sessions):
                    eligible_faculty = [f for f in self.instructors if f.subject == course]
                    selected_faculty = random.choice(eligible_faculty) if eligible_faculty else None
                    
                    self.classes_to_schedule.append({
                        "course": course,
                        "group": group,
                        "faculty": selected_faculty, 
                        "id": f"{group.name}-{course.name}-{i+1}"
                    })

        self.num_genes = len(self.classes_to_schedule)
        self.num_rooms = len(self.rooms)
        
        if self.num_rooms > 0:
            self.gene_space_max = (TOTAL_SLOTS * self.num_rooms) - 1
        else:
            self.gene_space_max = 0

    def decode_gene(self, gene_value):
        gene_value = int(gene_value)
        if self.num_rooms == 0: return None

        room_index = gene_value % self.num_rooms
        remainder = gene_value // self.num_rooms
        slot_index = remainder % SLOTS_PER_DAY
        day_index = remainder // SLOTS_PER_DAY
        
        if day_index >= len(DAYS): day_index = len(DAYS) - 1
        
        return {
            "day": DAYS[day_index],
            "slot": slot_index,
            "room": self.rooms[room_index],
            "raw_day_idx": day_index,
            "raw_slot_idx": slot_index
        }

    def fitness_func(self, ga_instance, solution, solution_idx):
        score = 0 

        # --- UPDATED PENALTIES ---
        PENALTY_HARD = 100000  # Hard Conflict
        PENALTY_SOFT = 300     # INCREASED: Force room spreading (was 10)
        PENALTY_LATE = 50      # Late classes

        faculty_schedule = {} 
        room_schedule = {}    
        group_schedule = {}
        room_usage_counts = defaultdict(int) 

        conflicting_groups_map = {
            "FULL CLASS": ["G1", "G2"],
            "G1": ["FULL CLASS"],
            "G2": ["FULL CLASS"]
        }

        for i, gene_val in enumerate(solution):
            if i >= len(self.classes_to_schedule): break
            
            class_info = self.classes_to_schedule[i]
            decoded = self.decode_gene(gene_val)
            if not decoded: continue 

            day = decoded['raw_day_idx']
            slot = decoded['raw_slot_idx']
            room = decoded['room']
            
            time_key = f"{day}-{slot}"

            # --- 1. ROOM CONFLICT ---
            room_key = f"{room.name}-{time_key}"
            if room_key in room_schedule:
                score -= PENALTY_HARD
            room_schedule[room_key] = True

            # --- 2. FACULTY CONFLICT ---
            if class_info['faculty']:
                fac_key = f"{class_info['faculty'].name}-{time_key}"
                if fac_key in faculty_schedule:
                    score -= PENALTY_HARD
                faculty_schedule[fac_key] = True

            # --- 3. GROUP CONFLICT ---
            current_group = class_info['group'].name.strip().upper()
            group_key = f"{current_group}-{time_key}"
            has_group_conflict = False
            
            if group_key in group_schedule: has_group_conflict = True
            
            for related in conflicting_groups_map.get(current_group, []):
                if f"{related}-{time_key}" in group_schedule:
                    has_group_conflict = True
            
            if has_group_conflict:
                score -= PENALTY_HARD
            
            group_schedule[group_key] = True
                
            # --- 4. ROOM TYPE & LOAD BALANCING ---
            c_type = class_info['course'].course_type.strip().upper()
            r_type = room.room_type.strip().upper() if room.room_type else "THEORY"
            
            if c_type == 'LAB' and r_type != 'LAB':
                score -= PENALTY_HARD 
            elif c_type == 'THEORY' and r_type == 'LAB':
                score -= PENALTY_HARD 
            
            # ** FIX: AGGRESSIVE LOAD BALANCING **
            # We track how many times a room is used.
            room_usage_counts[room.name] += 1
            usage = room_usage_counts[room.name]

            # If a room is used more than 2 times, start penalizing heavily.
            # usage 3 = -900 pts
            # usage 4 = -1200 pts
            # This forces the AI to move to Lab 2 and Lab 6 to save points.
            if usage > 2:
                score -= (usage * PENALTY_SOFT)

            # --- 5. TIME PREFERENCE ---
            if slot >= 5: 
                score -= PENALTY_LATE

        return score

    def run(self):
        if self.num_genes == 0 or self.num_rooms == 0: return []

        best_solution = None
        best_fitness = -999999
        
        # Give it 5 attempts to handle the randomness
        MAX_ATTEMPTS = 5
        
        for attempt in range(1, MAX_ATTEMPTS + 1):
            print(f"\n🔄 Attempt {attempt}/{MAX_ATTEMPTS}...")
            
            ga_instance = pygad.GA(
                num_generations=600,    
                num_parents_mating=6,
                fitness_func=self.fitness_func,
                sol_per_pop=60,         
                num_genes=self.num_genes,
                gene_type=int,
                init_range_low=0,
                init_range_high=self.gene_space_max,
                mutation_percent_genes=25,
                keep_parents=2 
            )

            try:
                ga_instance.run()
            except Exception as e:
                print(f"❌ Error: {e}")
                return []

            solution, solution_fitness, _ = ga_instance.best_solution()
            print(f"   Score: {solution_fitness}")

            if solution_fitness > best_fitness:
                best_fitness = solution_fitness
                best_solution = solution

            # --- THE FIX IS HERE ---
            # Any score higher than -90,000 means NO Hard Conflicts occurred.
            # (Because 1 conflict = -100,000)
            if best_fitness > -90000: 
                print("✅ Valid Schedule Found! (No Overlaps)")
                break
        
        # Final check before returning
        if best_fitness < -90000:
            print("⚠️ WARNING: Could not find a conflict-free schedule. best was:", best_fitness)

        # Decode logic remains the same...
        time_slots = {
            0: "8:40 - 9:40", 1: "9:40 - 10:40", 2: "10:40 - 11:40", 3: "11:40 - 12:40",
            4: "1:00 - 2:00", 5: "2:00 - 3:00", 6: "3:00 - 4:00", 7: "4:00 - 5:00"
        }
        day_order = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4}

        final_schedule = []
        for i, gene_val in enumerate(best_solution):
            if i >= len(self.classes_to_schedule): break
            decoded = self.decode_gene(gene_val)
            if not decoded: continue

            class_info = self.classes_to_schedule[i]
            final_schedule.append({
                "course": class_info['course'].name,
                "type": class_info['course'].course_type,
                "group": class_info['group'].name,
                "faculty": class_info['faculty'].name if class_info['faculty'] else "TBD",
                "room": decoded['room'].name,
                "day": decoded['day'],
                "slot": time_slots.get(decoded['slot'], f"Slot {decoded['slot'] + 1}"),
                "sort_day_idx": day_order.get(decoded['day'], 99),
                "sort_slot_idx": decoded['slot']
            })
            
        return sorted(final_schedule, key=lambda x: (x['sort_day_idx'], x['sort_slot_idx']))