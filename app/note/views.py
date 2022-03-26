# -*- coding: utf-8 -*-

import json

from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (
    CreateAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated
)
from rest_framework.response import Response

from note.authentication import AuthorAndAllAdmins, IsAuthenticatedOrReadOnly
from note.controller import (
    delete_user,
    get_all_users,
    get_user_name_by_id,
    update_user
)
from note.models import User, Note
from note.serializers import UserSerializer, NoteSerializer
from note.utils import sanitize_json_input


class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer


class UsersAPIView(RetrieveAPIView):
    permission_classes = (IsAdminUser, )
    serializer_class = UserSerializer

    def get(self, request):
        users = get_all_users()
        return Response(users)


class UserAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, AuthorAndAllAdmins)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def get(self, request, user_id):
        user_name = get_user_name_by_id(user_id)
        content = {'user is': user_name}
        return Response(content)

    @sanitize_json_input
    def put(self, request, *args, **kwargs):

        data = json.loads(self.request.body)
        uuid = kwargs.get('user_id')
        user_name = update_user(request, data, uuid)
        content = {'user {} has been updated'.format(self.request.user.name): user_name}
        return Response(content)

    def delete(self, request, *args, **kwargs):
        user_name = get_user_name_by_id(kwargs.get('user_id'))
        delete_user(kwargs.get('user_id'))
        content = 'User {} has been deleted'.format(user_name)
        return Response(content)


class NotesView(ListCreateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = NoteSerializer

    def get_queryset(self):
        visibility = self.request.user.is_authenticated
        tags = dict(self.request.query_params).get('tag')
        keyword = self.request.query_params.get('keyword')

        filter = Q(user_id=self.request.user.id) if visibility else Q(is_private=visibility)
        if tags:
            filter &= Q(tags__title__in=tags)

        if keyword:
            filter &= Q(title__icontains=keyword) | Q(body__icontains=keyword) | Q(tags__title__icontains=keyword)

        notes_obj = Note.objects.filter(filter).distinct()
        return notes_obj


class NoteView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = NoteSerializer

    def get_object(self):
        notes_obj = Note.objects.get(id=self.kwargs.get('id'))
        notes_obj = notes_obj if notes_obj.user_id == self.request.user or notes_obj.is_private == False else None
        return notes_obj

    @sanitize_json_input
    def put(self, request, *args, **kwargs):
        notes_obj = Note.objects.get(id=self.kwargs.get('id'))
        if notes_obj.user_id == self.request.user:
            return self.update(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def delete(self, request, *args, **kwargs):
        notes_obj = Note.objects.get(id=self.kwargs.get('id'))
        if notes_obj.user_id == self.request.user:
            return self.destroy(request, *args, **kwargs)
        else:
            raise PermissionDenied
