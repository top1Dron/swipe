from django.contrib import admin

from swipe.models import House, DeveloperHouse, Flat, Announcement, Promotion

admin.site.register(House)
admin.site.register(DeveloperHouse)
admin.site.register(Flat)
admin.site.register(Promotion)

class AnnouncementAdmin(admin.ModelAdmin):
    model = Announcement
    list_display = ('id', 'address', 'publication_date')

admin.site.register(Announcement, AnnouncementAdmin)