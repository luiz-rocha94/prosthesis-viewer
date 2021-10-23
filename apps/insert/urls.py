from django.urls import path
from apps.insert import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', login_required(views.New.as_view(), login_url="/login/")),
]
