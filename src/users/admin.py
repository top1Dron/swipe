from django.contrib import admin

from users.models import User, Client, Developer

admin.site.register(User)
admin.site.register(Client)
admin.site.register(Developer)
