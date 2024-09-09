from django.urls import path
from books import views

app_name = "books"

urlpatterns = [
    path("book/<int:book_id>", views.book_detail, name="book_detail"),
    path('search/', views.book_search, name='book_search'),
    path('categories/', views.categories, name='categories'),
    path('popular/', views.popular_books_view, name='popular_books'),
    path('new-releases/', views.new_releases_view, name='new_releases'),
]
