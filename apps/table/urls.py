from django.urls import path
from apps.table import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', login_required(views.Table.as_view(), login_url="/login/")),
]