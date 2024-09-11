from django.urls import path

from favorites import views

app_name = 'favorites'

urlpatterns = [
    path('', views.favorites, name='favorites'),

]
