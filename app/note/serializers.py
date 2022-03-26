# -*- coding: utf-8 -*-

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from note.models import User, Note, Tag


class UserSerializer(serializers.ModelSerializer):
    """Allows serialisation and deserialisation of `User` model objects.
    Attributes:
        name (CharField): [Required, Write_only].
        password (CharField): [Required, Write_only].
    """
    name = serializers.CharField(write_only=True, required=True)

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('password', 'name')

    def create(self, validated_data):
        """
        Create and return a `User` with an username and password.
        """
        user = User.objects.create(
            name=validated_data['name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

    def update(self, instance, validated_data):
        """
        Update and return updated `User`.
        """
        instance.name = validated_data.get('name', instance.name)

        instance.save()

        return instance



class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['title']


class NoteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Note
        fields = ('title', 'body', 'user_id', 'tags')
        extra_kwargs = {
            'user_id': {'required': False},
            'tags': {'required': False},
        }

    def create(self, validated_data):
        """
        Create and return a `User` with an username and password.
        """
        pass
        user = self.context['request'].user
        validated_data['user_id'] = user
        tags = []
        for tag in validated_data.pop('tags'):
            tag_obj, _ = Tag.objects.get_or_create(title=tag.get("title"))
            tags.append(tag_obj)

        note_obj = super().create(validated_data)
        note_obj.tags.set(tags)

        return note_obj

    def update(self, instance, validated_data):
        tags = []
        if 'tags' in validated_data:
            for tag in validated_data.pop('tags'):
                obj, _ = Tag.objects.get_or_create(title=tag.get("title"))
                tags.append(obj)
            instance.tags.set(tags)

        instance.title = validated_data.get("title")
        instance.body = validated_data.get("body")
        instance.save()

        return instance

    def to_representation(self, instance):
        """Return a serialised dict containing `UsageType` data"""
        data = super().to_representation(instance)
        data.pop('user_id')
        return data


