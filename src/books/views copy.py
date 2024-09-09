import logging
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user
from django.http import JsonResponse, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from books.models import Book
from favorites.models import Favorite
from rentals.models import Rental
from reviews.forms import RatingForm, ReviewForm
from reviews.models import Review, Rating


logger = logging.getLogger(__name__)


async def book_search(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return JsonResponse({'books': []})

    books = await sync_to_async(list)(Book.objects.filter(title__icontains=query))

    results = [
        {
            'id': book.id,
            'title': book.title,
            'cover_image': book.cover_image.url if book.cover_image else None,
            'authors': await sync_to_async(list)(book.authors.all()),
            'language': await sync_to_async(lambda: book.language)(),
            'categories': await sync_to_async(list)(book.categories.all())
        }
        for book in books
    ]

    return await sync_to_async(render)(request, 'books/book_list.html', {'books': results})


async def book_detail(request: HttpRequest, book_id: int) -> HttpResponse:
    try:
        book = await sync_to_async(Book.objects.select_related('language')
                                   .prefetch_related('authors', 'categories').get)(id=book_id)
        user_has_active_rental = await sync_to_async(Rental.objects.filter)(user=request.user, returned=False).exists()

    except Book.DoesNotExist:
        logger.error(f"Book with id {book_id} does not exist.")
        return HttpResponseBadRequest("Book not found.")

    def get_referer():
        return request.headers.get('Referer', '/')

    def set_previous_page_in_session(previous_page):
        request.session['previous_page'] = previous_page

    # Получение предыдущей страницы и установка значения в сессии
    previous_page = await sync_to_async(get_referer)()
    await sync_to_async(set_previous_page_in_session)(previous_page)

    user = await sync_to_async(get_user)(request)

    unique_reviewers_count = await sync_to_async(Review.objects.count_unique_reviewers_for_book)(book)
    unique_users_count = await sync_to_async(Rating.objects.count_unique_users_for_book)(book)
    try:
        current_rating = await sync_to_async(Rating.objects.get)(user=user, book=book)
    except Rating.DoesNotExist:
        current_rating = None

    if request.method == "POST":
        if "submit_review" in request.POST:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.book = book
                review.user = user
                await sync_to_async(review.save)()
                return await sync_to_async(redirect)('books:book_detail', book_id=book.id)
        elif 'submit_rating' in request.POST:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                score = rating_form.cleaned_data['score']
                # Обновление или создание нового рейтинга
                await sync_to_async(Rating.objects.update_or_create)(
                    user=user, book=book, defaults={'score': score})
                # Пересчет среднего рейтинга
                average_rating = await sync_to_async(Rating.objects.average_rating_for_book)(book)
                return await sync_to_async(redirect)('books:book_detail', book_id=book.id)

        elif 'add_to_favorites' in request.POST:
            await sync_to_async(Favorite.objects.add_to_favorites)(user=request.user, book=book)
            return redirect('books:book_detail', book_id=book.id)
        elif 'remove_from_favorites' in request.POST:
            await sync_to_async(Favorite.objects.remove_from_favorites)(user=request.user, book=book)
            return redirect('books:book_detail', book_id=book.id)
        elif 'rent_book' in request.POST:
            if not book.available:
                return HttpResponseBadRequest("Book is not available for rental.")
            try:
                await sync_to_async(Rental.objects.create)(
                    user=user,
                    book=book
                )
                book.available = False
                await sync_to_async(book.save)()
                return await sync_to_async(redirect)('books:book_detail', book_id=book.id)
            except ValueError as e:
                return HttpResponseBadRequest(str(e))
    else:
        review_form = ReviewForm()
        rating_form = RatingForm()

    authors = await sync_to_async(list)(book.authors.all())
    categories = await sync_to_async(list)(book.categories.all())
    average_rating = await sync_to_async(Rating.objects.average_rating_for_book)(book)
    is_favorite = await sync_to_async(Favorite.objects.is_favorite)(user=request.user, book=book)
    reviews = await sync_to_async(list)(book.reviews.all())

    context = {
        'book': book,
        'review_form': review_form,
        'rating_form': rating_form,
        'authors': authors,
        'categories': categories,
        'is_available': book.available,
        'average_rating': average_rating or 0,
        'unique_users_count': unique_users_count,
        'unique_reviewers_count': unique_reviewers_count,
        'is_favorite': is_favorite,
        'reviews': reviews,
        'current_rating': current_rating,
    }

    return await sync_to_async(render)(request, 'books/book_detail.html', context)
