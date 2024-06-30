from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('category/<slug:category_slug>/', views.home, name='category_books'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('all_books', views.all_books, name='all_books'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:borrow_id>/', views.return_book, name='return_book'),
    path('deposit/', views.deposit_money, name='deposit_money'),
    path('add_review/<int:book_id>/', views.add_review, name='add_review'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('category/<slug:category_slug>/', views.category_books, name='category_books'),
]
