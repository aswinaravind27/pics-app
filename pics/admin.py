from django.contrib import admin
from .models import Customers,Photo,Albums,FavAlbums
# Register your models here.

admin.site.register(Customers)

admin.site.register(Photo)

admin.site.register(Albums)

admin.site.register(FavAlbums)