from django.urls import path

from . import views

app_name = "desk"

urlpatterns = [
    path("ask/", views.ask, name="ask"),
    path("educators/", views.educators, name="educators"),
    path("educators/apply/", views.apply, name="apply"),
    path("educators/requests/<int:pk>/done/", views.resolve, name="resolve"),
]
