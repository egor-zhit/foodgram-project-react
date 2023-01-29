from rest_framework import serializers
from recipes.models import TagModel

class TagSerialiser(serializers.ModelSerializer):

    class Meta():
       model = TagModel
       fields = (
        'name',
        'color',
        'slug',
       )