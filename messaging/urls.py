from django.urls import path

from . import views

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("start/<int:listing_id>/", views.start_conversation, name="start_conversation"),
    path("<int:pk>/", views.thread, name="thread"),
    path("<int:pk>/send/", views.send_message, name="send_message"),
    path("<int:pk>/poll/", views.poll_messages, name="poll_messages"),
]
