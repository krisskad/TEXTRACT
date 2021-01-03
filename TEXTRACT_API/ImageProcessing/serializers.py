from rest_framework import serializers
from .models import ImageRecord
from django.contrib.auth.models import User


class ImageSerializer(serializers.ModelSerializer):  # create class to serializer model
    creator = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = ImageRecord
        fields = ('Image', 'creator')


class UserSerializer(serializers.ModelSerializer):  # create class to serializer user_model
    ImageMetadata = serializers.PrimaryKeyRelatedField(many=True, queryset=ImageRecord.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username')
