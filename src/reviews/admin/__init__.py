from app.admin import ModelAdmin, admin
from reviews.admin.admin import RatingAdmin, ReviewAdmin

__all__ = [
    "admin",
    "ModelAdmin",
    "ReviewAdmin",
    "RatingAdmin",
]
