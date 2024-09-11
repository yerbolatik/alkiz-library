from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rentals.models import Rental
from subscriptions.models import Subscription


def library_view(request):
    user = request.user

    # Получение информации о подписке
    subscription = get_object_or_404(Subscription, user=user)
    subscription_status = 'Активна' if subscription.is_active() else 'Неактивна'
    subscription_end_date = subscription.end_date.strftime(
        "%d.%m.%Y") if subscription.end_date else 'Бессрочная'

    # Получение текущей арендованной книги
    current_rental = Rental.objects.filter(user=user, returned=False).first()
    rented_book = None
    if current_rental:
        rented_book = {
            'title': current_rental.book.title,
            'cover_url': current_rental.book.cover_image.url if current_rental.book.cover_image else 'default_cover_url',
            'author': ', '.join(str(author) for author in current_rental.book.authors.all()),
            'return_date': current_rental.end_date.strftime("%d.%m.%Y"),
            'remaining_time': (current_rental.end_date - timezone.now()).days
        }

    context = {
        'subscription': subscription,
        'subscription_status': subscription_status,
        'subscription_end_date': subscription_end_date,
        'rented_book': rented_book,
    }

    return render(request, 'rentals/library.html', context)


def rental_history_view(request):
    user = request.user

    # Получение всех арендованных книг пользователя, которые уже возвращены
    rentals = Rental.objects.filter(
        user=user, returned=True).order_by('-end_date')

    # Подготовка данных для шаблона
    rental_history = []
    for rental in rentals:
        rental_duration = (rental.end_date - rental.start_date).days if rental.returned else (
            timezone.now() - rental.start_date).days

        rental_history.append({
            'title': rental.book.title,
            'cover_url': rental.book.cover_image.url if rental.book.cover_image else 'default_cover_url',
            'author': ', '.join(str(author) for author in rental.book.authors.all()),
            'start_date': rental.start_date.strftime("%d.%m.%Y"),
            'return_date': rental.end_date.strftime("%d.%m.%Y"),
            'rental_duration': rental_duration
        })

    context = {
        'rental_history': rental_history,
    }

    return render(request, 'rentals/rental_history.html', context)
