from django.urls import path

from . import views

app_name = "service"
urlpatterns = [
    path("create", views.create, name="create"),
    path("get/<int:user_id>", views.get, name="get"),
]
