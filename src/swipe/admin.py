from django.contrib import admin

from swipe.models import House, DeveloperHouse, Flat, Announcement

admin.site.register(House)
admin.site.register(DeveloperHouse)
admin.site.register(Flat)

class AnnouncementAdmin(admin.ModelAdmin):
    model = Announcement
    list_display = ('id', 'address', 'publication_date')

admin.site.register(Announcement, AnnouncementAdmin)