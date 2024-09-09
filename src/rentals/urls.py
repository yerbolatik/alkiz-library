from django.urls import path
from rentals import views

app_name = 'rentals'

urlpatterns = [
    path('', views.library_view, name='library'),
    path('rental-history/', views.rental_history_view, name='rental_history'),
]
