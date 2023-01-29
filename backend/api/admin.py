from django.contrib import admin

from recipes.models import TagModel

#@admin.register(TagModel)
# class TagAdmin(admin.ModelAdmin):
  #          list_display = (
   #             ''
#            )
admin.site.register(TagModel)
