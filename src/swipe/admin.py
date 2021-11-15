from django.contrib import admin

from swipe.models import House, DeveloperHouse, Flat, Announcement, Promotion, AnnouncementImage

admin.site.register(House)
admin.site.register(DeveloperHouse)
admin.site.register(Flat)
admin.site.register(Promotion)
admin.site.register(AnnouncementImage)

class AnnouncementAdmin(admin.ModelAdmin):
    model = Announcement
    list_display = ('id', 'address', 'publication_date')

admin.site.register(Announcement, AnnouncementAdmin)