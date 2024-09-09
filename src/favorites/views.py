from asgiref.sync import sync_to_async
from django.contrib.auth import get_user
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect

from books.models import Book
from favorites.models import Favorite
from rentals.models import Rental
from reviews.models import Rating


async def favorites(request: HttpRequest) -> HttpResponse:
    user = await sync_to_async(get_user)(request)

    user_has_active_rental = await sync_to_async(
        lambda: Rental.objects.filter(
            user=user, returned=False).exists()
    )()

    if request.method == "POST":
        book_id = request.POST.get('book_id')
        if not book_id:
            return HttpResponseBadRequest("Book ID is missing.")

        try:
            book = await sync_to_async(Book.objects.get)(id=book_id)
        except Book.DoesNotExist:
            return HttpResponseBadRequest("Book not found.")

        if 'add_to_favorites' in request.POST:
            await sync_to_async(Favorite.objects.add_to_favorites)(user=user, book=book)
        elif 'remove_from_favorites' in request.POST:
            await sync_to_async(Favorite.objects.remove_from_favorites)(user=user, book=book)

        # Перенаправление на ту же страницу после добавления/удаления
        return redirect('favorites:favorites')

    favorite_books = await sync_to_async(Favorite.objects.favorite_books_for_user)(user)
    book_details = await sync_to_async(get_book_details)(favorite_books, user)

    context = {
        'book_details': book_details,
        "user_has_active_rental": user_has_active_rental,

    }

    return await sync_to_async(render)(request, 'favorites/favorites.html', context)


def get_book_details(favorite_books, user):
    book_details = []
    for favorite in favorite_books:
        book = favorite.book
        authors = list(book.authors.all())
        language = book.language
        average_rating = Rating.objects.average_rating_for_book(book)
        is_favorite = Favorite.objects.is_favorite(user=user, book=book)

        book_details.append({
            'book': book,
            'authors': authors,
            'language': language,
            'average_rating': average_rating,
            'is_favorite': is_favorite,
        })
    return book_details
