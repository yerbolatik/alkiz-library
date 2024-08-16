from app.admin import ModelAdmin, admin
from books.admin.admin import AuthorAdmin, BookAdmin, CategoryAdmin

__all__ = [
    "admin",
    "ModelAdmin",
    "AuthorAdmin",
    "BookAdmin",
    "CategoryAdmin",
]
