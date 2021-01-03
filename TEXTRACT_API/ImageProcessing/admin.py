from django.contrib import admin
from .models import ImageRecord


# Register your models here.
class AuthorAdmin(admin.ModelAdmin):
    pass


admin.site.register(ImageRecord, AuthorAdmin)
