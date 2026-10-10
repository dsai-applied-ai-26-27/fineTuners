from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("delete/", views.delete_account, name="delete"),
    # Answers 404 unless DEBUG is on: see the view.
    path("dev-login/", views.dev_login, name="dev_login"),
]
