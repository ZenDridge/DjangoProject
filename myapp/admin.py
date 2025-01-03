from django.contrib import admin
from .models import User, Event

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'sid', 'staff', 'admin', 'joined')
    search_fields = ('first_name', 'middle_name', 'last_name', 'email', 'sid')
    list_filter = ('staff', 'admin', 'active')
    ordering = ('-joined',)

    def full_name(self, obj):
        return f"{obj.first_name} {obj.middle_name} {obj.last_name}"
    full_name.short_description = 'Name'

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start', 'end', 'owner')
    search_fields = ('title', 'desc')
    list_filter = ('start', 'end', 'owner')
    ordering = ('start',)