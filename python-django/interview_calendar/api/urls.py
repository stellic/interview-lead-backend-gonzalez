from django.urls import path

from . import views

urlpatterns = [
    path("users/", views.get_users, name="get_users"),
    path("event/<str:user_id>", views.get_events, name="get_events"),
    path("event/create/<str:instructor_id>/<str:student_id>/<str:start>/<str:end>/<str:name>", views.insert_event, name="insert_event"),

    path(
        "users/<int:user_id>/calendar/free/", views.get_user_calendar_free, name="get_user_calendar_free",
    ),
]
