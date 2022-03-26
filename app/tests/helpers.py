# -*- coding: utf-8 -*-

import pytest
import pytz

from datetime import datetime
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient

from note.models import User, Note, Tag


@pytest.fixture
def api_client_admin():
    user = User.objects.create(name='admin', password='js.sj', is_superuser=1, is_staff=1)
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    print(refresh)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    return client


def create_user(user_name):
    user = User.objects.create(name=user_name, password='js.sj')
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    print(refresh)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    return client, user


def get_user(user_name):
    user = User.objects.get(name=user_name)
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    print(refresh)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    return client, user


def get_time_now():
    now = datetime.now(tz=pytz.utc)
    formatted_datetime = now.isoformat()
    return formatted_datetime


def reverse_querystring(view, urlconf=None, args=None, kwargs=None, current_app=None, query_kwargs=None, postfix=None):
    '''Custom reverse to handle query strings.
    Usage:
        reverse('app.views.my_view', kwargs={'pk': 123}, query_kwargs={'search': 'Bob'}, postfix='<usage_id>')
    '''
    base_url = reverse(view, urlconf=urlconf, args=args, kwargs=kwargs, current_app=current_app)
    if postfix:
        base_url = '{}/{}/'.format(base_url, postfix)
    if query_kwargs:
        return '{}?{}'.format(base_url, urlencode(query_kwargs))
    return base_url


@pytest.fixture
def superuser():
    user = User.objects.create(name='johndoe', password='js.sj', is_superuser=1, is_staff=1)
    return user


def create_notes(user_id, title, body, is_private=True, tags=[]):
    note = Note.objects.create(user_id=user_id, title=title, body=body, is_private=is_private)
    tag_list = []
    for tag in tags:
        tag_obj, _ = Tag.objects.get_or_create(title=tag.get("title"))
        tag_list.append(tag_obj)
    note.tags.set(tag_list)
    return note
