import datetime
import zoneinfo

from django.db import models

# Create your models here.
class Person(models.Model):
    class Meta:
        app_label = 'interview_calendar'
        db_table  = 'person'

    # assumes "width of 16" for [S|I][0-9]*15, S for student, I for instructor
    person_id    = models.CharField(blank=False, null=False, max_length=16, primary_key=True, default="S000000000000000")
    first_name = models.TextField(default="fnu")    
    last_name  = models.TextField(blank=False, null=False, default="Smith")

    
class Event(models.Model):
    class Meta:
        app_label = 'interview_calendar'
        db_table  = 'event'

    event_id       = models.BigAutoField(blank=False, null=False, primary_key=True, db_index=True)
    student        = models.ForeignKey(Person, null=True, on_delete=models.CASCADE, related_name="student_events")
    instructor     = models.ForeignKey(Person, null=True, on_delete=models.CASCADE, related_name="instructor_events")
    epoch_start    = models.IntegerField(blank=False, null=False, db_index=True, default=0) 
    epoch_end      = models.IntegerField(blank=False, null=False, db_index=True, default=0)
    event_start_datetime = models.TextField(blank=False, null=False, db_index=True, default="")
    event_end_datetime = models.TextField(blank=False, null=False, db_index=True, default="")
    name           = models.TextField(blank=False, null=False, default="class")
    day_of_week    = models.TextField(blank=False, null=False, default="monday")
    created_on     = models.DateTimeField(auto_now_add=True)

    @classmethod
    def insert_event(cls, instructor_id:str, student_id:str, event_name:str, start:str, end:str)->bool:
        pass
    
    def __str__(self):
        return "Event {} '{}' '{}'".format(self.event_id, self.epoch_start, self.epoch_end)
    

