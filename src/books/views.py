import logging
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user
from django.db.models import Count
from django.http import JsonResponse, HttpRequest, HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from books.forms import BookFilterForm
from books.models import Book, Category
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
        user_has_active_rental = await sync_to_async(
            lambda: Rental.objects.filter(
                user=request.user, returned=False).exists()
        )()

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
            if user_has_active_rental:
                return HttpResponseBadRequest("You already have an active rental.")
            if not book.available:
                return HttpResponseBadRequest("Book is not available for rental.")
            try:
                await sync_to_async(Rental.objects.create)(user=user, book=book)
                book.available = False
                await sync_to_async(book.save)()
                return redirect('books:book_detail', book_id=book.id)
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
        'user_has_active_rental': user_has_active_rental,
    }

    return await sync_to_async(render)(request, 'books/book_detail.html', context)


async def categories(request: HttpRequest) -> HttpResponse:
    # Получение категорий
    categories = await sync_to_async(list)(Category.objects.all())

    # Изначально QuerySet для книг
    books_query = Book.objects.all()
    books = books_query

    # Получение выбранной категории и фильтрация по ней
    category_id = await sync_to_async(request.GET.get)('category')
    if category_id:
        try:
            selected_category = await sync_to_async(Category.objects.get)(id=category_id)
            books_query = books.filter(categories=selected_category)
        except Category.DoesNotExist:
            raise Http404("Категория не найдена")
    else:
        selected_category = None
    logger.debug(f"Selected category ID: {category_id}")

    form = BookFilterForm(request.GET)
    if await sync_to_async(form.is_valid)():
        author = await sync_to_async(form.cleaned_data.get)('author')
        category = await sync_to_async(form.cleaned_data.get)('category')
        language = await sync_to_async(form.cleaned_data.get)('language')

        available_filter = form.cleaned_data['available']
        if available_filter == 'available':
            books = books.filter(available=True)
        elif available_filter == 'not_available':
            books = books.filter(available=False)

        if author:
            books = books.filter(authors=author)
        if category:
            books = books.filter(categories=category)
        if language:
            books = books.filter(language=language)

    # Преобразование QuerySet в список
    books = await sync_to_async(list)(books.distinct())
    logger.info(f"Books: {books}")
    user = request.user

    # Получение деталей книг
    book_details = []
    if books:
        for book in books:
            authors = await sync_to_async(list)(book.authors.all())
            language = await sync_to_async(lambda: book.language)()
            average_rating = await sync_to_async(Rating.objects.average_rating_for_book)(book)
            is_favorite = await sync_to_async(lambda: Favorite.objects.filter(user=user, book=book).exists)()

            book_details.append({
                'book': book,
                'authors': authors,
                'language': language,
                'average_rating': average_rating,
                'is_favorite': is_favorite,
            })

    context = {
        'categories': categories,
        'selected_category': selected_category,
        'books': books,
        'book_details': book_details,
        'form': form,
    }
    return await sync_to_async(render)(request, 'books/categories.html', context)


def popular_books_view(request):
    """
    Отображает книги, которые были арендованы больше всего раз.
    """
    popular_books = Book.objects.annotate(
        total_rentals=Count('rentals')
    ).order_by('-total_rentals')[:10]

    book_details = []
    for book in popular_books:
        average_rating = Rating.objects.average_rating_for_book(book)

        book_details.append({
            'book': book,
            'average_rating': average_rating,
        })

    context = {
        'books': book_details,
    }
    return render(request, 'books/popular_books.html', context)


def new_releases_view(request):
    """
    Отображает последние добавленные книги.
    """
    new_releases = Book.objects.order_by(
        '-id')[:10]

    book_details = []
    for book in new_releases:
        average_rating = Rating.objects.average_rating_for_book(book)

        book_details.append({
            'book': book,
            'average_rating': average_rating,
        })

    context = {
        'books': book_details,
    }
    return render(request, 'books/new_releases.html', context)
