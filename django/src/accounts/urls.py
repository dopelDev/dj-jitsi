from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("meet/create/", views.create_meeting, name="create_meeting"),
    path("meet/<int:pk>/", views.meeting_detail, name="meeting_detail"),
    path("requests/", views.admin_requests, name="admin_requests"),
    path("requests/<int:pk>/", views.request_detail, name="request_detail"),
    path("requests/<int:pk>/approve/", views.approve_request, name="approve_request"),
    path("requests/<int:pk>/reject/", views.reject_request, name="reject_request"),
    path("requests/<int:pk>/reset/", views.reset_request, name="reset_request"),
]
