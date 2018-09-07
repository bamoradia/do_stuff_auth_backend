from django.contrib import admin
from .models import UserProfile, Event, Category, UserEvent, UserCategory, EventCategory


# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Event)
admin.site.register(Category)
admin.site.register(UserEvent)
admin.site.register(UserCategory)
admin.site.register(EventCategory)