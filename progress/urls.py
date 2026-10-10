from django.urls import path

from . import views

app_name = "progress"

urlpatterns = [
    path("sync/", views.sync_view, name="sync"),
]
