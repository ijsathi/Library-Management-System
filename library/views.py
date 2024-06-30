from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.utils import timezone
from django.core.mail import send_mail
from .models import Book, Borrow, Review, UserProfile, Category
from .forms import DepositForm, ReviewForm, BorrowForm, ReturnForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.conf import settings
from django.contrib import messages


def home(request):
    categories = Category.objects.all()
    books = Book.objects.all()
    return render(request, 'library/home.html', {'categories': categories, 'books': books})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')


@login_required
def profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        borrows = Borrow.objects.filter(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None
        borrows = None  
    
    return render(request, 'library/profile.html', {'user_profile': user_profile, 'borrows': borrows})
# @login_required
# def profile(request):
#     user_profile, created = UserProfile.objects.get_or_create(user=request.user)
#     borrows = Borrow.objects.filter(user=request.user)
#     return render(request, 'library/profile.html', {'user_profile': user_profile, 'borrows': borrows})

@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    user_profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = BorrowForm(request.POST)
        if form.is_valid() and book.available and user_profile.balance >= book.borrowing_price:
            user_profile.balance -= book.borrowing_price
            user_profile.save()
            Borrow.objects.create(user=request.user, book=book)
            book.available = False
            book.save()
            send_mail(
                'Book Borrowed',
                f'You have borrowed the book {book.title}.',
                'Library_Management',
                [request.user.email],
                fail_silently=False,
            )
            return redirect('home')
    else:
        form = BorrowForm()
    return render(request, 'library/borrow_book.html', {'book': book, 'form': form})

@login_required
def return_book(request, borrow_id):
    borrow = get_object_or_404(Borrow, pk=borrow_id)
    user_profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ReturnForm(request.POST)
        if form.is_valid():
            user_profile.balance += borrow.book.borrowing_price
            user_profile.save()
            borrow.returned = True
            borrow.return_date = timezone.now()
            borrow.save()
            borrow.book.available = True
            borrow.book.save()
            send_mail(
                'Book Returned',
                f'You have returned the book {borrow.book.title}. Thank You! Stay with us):',
                'Library_Management',
                [request.user.email],
                fail_silently=False,
            )
            return redirect('home')
    else:
        form = ReturnForm()
    return render(request, 'library/return_book.html', {'borrow': borrow, 'form': form})

@login_required
def deposit_money(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            user_profile.balance += amount
            user_profile.save()
            return redirect('profile')  
    else:
        form = DepositForm()

    return render(request, 'library/deposit_money.html', {'form': form})

# def book_detail(request, book_id):
#     book = get_object_or_404(Book, pk=book_id)
#     reviews = Review.objects.filter(book=book)
#     return render(request, 'library/book_detail.html', {'book': book, 'reviews': reviews})

@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        if 'borrow' in request.POST:
            user_profile = get_object_or_404(UserProfile, user=request.user)
            if book.available and user_profile.balance >= book.borrowing_price:
                user_profile.balance -= book.borrowing_price
                user_profile.save()

                book.available = False
                book.save()

                Borrow.objects.create(user=request.user, book=book)

                send_mail(
                    'Book Borrowed Successfully',
                    f'You have successfully borrowed {book.title}. Thanks for taking it, stay with us!',
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email]
                )

                return redirect('book_detail', book_id=book.id)
            else:
                messages.warning(request, "Book is not available or you have insufficient balance.")
                return redirect('book_detail', book_id=book.id)
        elif 'review' in request.POST:
            form = ReviewForm(request.POST)
            if form.is_valid():
                Review.objects.create(
                    book=book,
                    user=request.user,
                    rating=form.cleaned_data['rating'],
                    review=form.cleaned_data['comment']
                )
                messages.success(request, "Your review has been submitted.")
                return redirect('book_detail', book_id=book.id)
    else:
        form = ReviewForm()

    reviews = book.reviews.all()
    return render(request, 'library/book_detail.html', {
        'book': book,
        'form': form,
        'reviews': reviews
    })

@login_required
def add_review(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.cleaned_data['review']
            Review.objects.create(user=request.user, book=book, review=review)
            return redirect('book_detail', book_id=book_id)
    else:
        form = ReviewForm()
    return render(request, 'library/add_review.html', {'form': form, 'book': book})

def category_books(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    books = category.book_set.all() 
    categories = Category.objects.all() 
    context = {
        'category': category,
        'books': books,
        'categories': categories,
        'selected_category_slug': category_slug,  
    }
    return render(request, 'library/home.html', context)

def all_books(request):
    books = Book.objects.all()
    return render(request, 'library/books.html', {'books': books})