from django.contrib import admin
from .models import Post, Category, Option, Poll

admin.site.register(Post)
admin.site.register(Category)
class OptionInline(admin.TabularInline):
    model = Option
    extra = 3

class PollAdmin(admin.ModelAdmin):
    inlines = [OptionInline]

admin.site.register(Poll, PollAdmin)

# Register your models here.
