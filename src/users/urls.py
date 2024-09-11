from django.urls import path
from users import views

app_name = "users"

urlpatterns = [
    path('profile/', views.update_profile, name='update_profile'),
]
