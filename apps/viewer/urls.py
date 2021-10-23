from django.urls import path
from apps.viewer import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', login_required(views.TcView.as_view(), login_url="/login/")),
]