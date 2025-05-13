from dateutil import parser
from django.db import connection
from django.db.models import Q
from django.http import JsonResponse
from http import HTTPStatus

from .schedule import calendar_free
from api.models import Person, Event


def check_conflict(instructor_id, student_id, epoch_start, epoch_end):
    with connection.cursor() as cursor:
        # ick...not very elegant or easily exentisble.  refactor.
        if (student_id is not None and student_id.strip() != "" and student_id != "none") and \
           (instructor_id is not None and instructor_id.strip() != "" or instructor_id != "none"):
            cursor.execute("select count(*) as cnt from event where (GREATEST(epoch_start, %s) < LEAST(epoch_end, %s)) and (instructor_id=%s or student_id=%s)", [int(epoch_start), int(epoch_end), instructor_id, student_id])
        elif (student_id is None or student_id.strip() == "" or student_id == "none"):
            cursor.execute("select count(*) as cnt from event where (GREATEST(epoch_start, %s) < LEAST(epoch_end, %s)) and instructor_id=%s", [int(epoch_start), int(epoch_end), instructor_id])
        elif (instructor_id is None or instructor_id.strip() == "" or instructor_id == "none"):
            cursor.execute("select count(*) as cnt from event where (GREATEST(epoch_start, %s) < LEAST(epoch_end, %s)) and student_id=%s", [int(epoch_start), int(epoch_end), student_id])
        else:
            # if there is no student or instructor, then I guess there are no conflicts; leave it to the server to
            # have a more coherent response
            return 0 

        return cursor.fetchone()[0]
    



def get_users(request):
    persons = Person.objects.all()
    return JsonResponse(
        [
            {"person_id":person.person_id, "name": f"{person.last_name}, {person.first_name}"} for person in persons
        ],
        status=200, safe=False
    )

def get_events(request, user_id):
    found_events = Event.objects.filter(Q(instructor_id=user_id) | Q(student_id=user_id))

    print(
        [
            {"name":event.name, "start":event.event_start_datetime, "end":event.event_end_datetime, "student":event.student_id, "instructor":event.instructor_id
             } for event in found_events
        ]
    )

    return JsonResponse( [
        {"name":event.name, "start":event.event_start_datetime, "end":event.event_end_datetime, "student":event.student_id, "instructor":event.instructor_id
            } for event in found_events
    ]
                         , safe=False)
    
            
def insert_event(request, instructor_id, student_id, start, end, name):
    start_date  = parser.isoparse(start)
    end_date    = parser.isoparse(end)

    # convert these into epoch seconds; default converts to utc before converting to seconds since epoch
    epoch_start = start_date.timestamp()
    epoch_end   = end_date.timestamp()

    conflicts = check_conflict(instructor_id, student_id, epoch_start, epoch_end)
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    if conflicts:
        return JsonResponse([], status=409, safe=False)
    elif (student_id is None or student_id.strip() == "" or student_id == "none") and (instructor_id is None or instructor_id.strip() == "" or instructor_id == "none"):
        return JsonResponse([], status=400, safe=False)
    else:
        new_event = Event()
        new_event.name             = name
        if student_id is not None and student_id.strip() != "" and student_id != "none":
            new_event.student          = Person.objects.get(person_id=student_id)

        if instructor_id is not None and instructor_id.strip() !="" and instructor_id != "none":
            new_event.instructor       = Person.objects.get(person_id=instructor_id)
        new_event.epoch_start      = epoch_start
        new_event.epoch_end        = epoch_end
        new_event.event_start_datetime = start
        new_event.event_end_datetime   = end
        new_event.day_of_week      = day_names[start_date.weekday()]
        new_event.save()
        return JsonResponse([], status=200, safe=False)
    

def get_user_calendar_free(request, user_id):
    return JsonResponse(calendar_free(user_id), safe=False)
