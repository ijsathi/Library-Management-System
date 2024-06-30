from django.contrib import admin
from .models import Book, Borrow, Review, UserProfile, Category

admin.site.register(Book)
admin.site.register(Borrow)
admin.site.register(Review)
admin.site.register(UserProfile)
admin.site.register(Category)
