import json
import pytest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from tests.helpers import (
    create_notes,
    create_user,
    get_time_now,
    get_user,
    reverse_querystring
)


@pytest.mark.django_db
class TestUsageTypes:

    def test_create_notes(self):
        api_client, user_id = create_user('Penny')

        url = reverse('notes')
        data = json.dumps({"title": "Test Note",
                           "body": "Hello this is my First Note",
                           "tags": [{"title": "blog"}, {"title":"thoughts"}]
                           })
        response = api_client.post(url, data=data, content_type="application/json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_non_auth_user_fails(self):
        non_auth_client = APIClient()
        url = reverse('notes')
        data = json.dumps({"title": "Test Note",
                           "body": "Hello this is my First Note",
                           "tags": [{"title": "blog"}, {"title": "thoughts"}]
                           })
        response = non_auth_client.post(url, data=data, content_type="application/json")
        # assert response.status_code == status.HTTP_201_CREATED
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_all_notes(self):
        api_client, user_id = create_user('Penny')

        create_notes(user_id, "Test Note", "Hello this is my First Note", True,
                     [{"title": "blog"}, {"title": "thoughts"}])

        create_notes(user_id, "Test Note 2", "Hello this is my Second Note", False,
                     [{"title": "blog"}, {"title": "thoughts"}])

        url = reverse_querystring('notes')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_get_all_non_auth_user(self):
        non_auth_client = APIClient()
        _, user_id = create_user('Penny')

        create_notes(user_id, "Test Note", "Hello this is my First Note", True,
                     [{"title": "blog"}, {"title": "thoughts"}])

        create_notes(user_id, "Test Note 2", "Hello this is my Second Note", False,
                     [{"title": "blog"}, {"title": "thoughts"}])

        url = reverse_querystring('notes')
        response = non_auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_get_private_notes_wrong_user_fails(self):
        api_client_1, user_id_1 = create_user('Penny')
        api_client_2, user_id_2 = create_user('Howard')

        note = create_notes(user_id_1, "Test Note", "Hello this is my First Note", True,
                     [{"title": "blog"}, {"title": "thoughts"}])


        url = reverse('note', args=[note.id])

        response = api_client_2.get(url)
        assert response.data['user_id'] == None
        assert response.data['body'] == ''
        assert response.data['title'] == ''
        assert response.data['tags'] == []

    def test_update_note(self):
        api_client, user_id = create_user('Penny')

        note = create_notes(user_id, "Test Note", "Hello this is my First Note", True,
                            [{"title": "blog"}, {"title": "thoughts"}])

        url = reverse('note', args=[note.id])

        data = json.dumps({"title": "Test Note Update",
                           "body": "Hello this is my updated Note",
                           "tags": [{"title": "space"}, {"title": "science"}]
                           })
        response = api_client.put(url, data=data, content_type='application/json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == "Test Note Update"
        assert response.data['body'] == "Hello this is my updated Note"

    def test_update_note_non_auth_user_fails(self):
        non_auth_client = APIClient()
        api_client, user_id = create_user('Penny')

        note = create_notes(user_id, "Test Note", "Hello this is my First Note", True,
                            [{"title": "blog"}, {"title": "thoughts"}])

        url = reverse('note', args=[note.id])

        data = json.dumps({"title": "Test Note Update",
                           "body": "Hello this is my updated Note",
                           "tags": [{"title": "space"}, {"title": "science"}]
                           })
        response = non_auth_client.put(url, data=data, content_type='application/json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_note_wrong_user_fails(self):
        api_client_1, user_id_1 = create_user('Penny')
        api_client_2, user_id_2 = create_user('Howard')

        note = create_notes(user_id_1, "Test Note", "Hello this is my First Note", True,
                            [{"title": "blog"}, {"title": "thoughts"}])

        url = reverse('note', args=[note.id])

        data = json.dumps({"title": "Test Note Update",
                           "body": "Hello this is my updated Note",
                           "tags": [{"title": "space"}, {"title": "science"}]
                           })
        response = api_client_2.put(url, data=data, content_type='application/json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_note(self):
        api_client, user_id = create_user('Penny')

        note = create_notes(user_id, "Test Note", "Hello this is my First Note", True,
                     [{"title": "blog"}, {"title": "thoughts"}])

        url = reverse('note', args=[note.id])
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = api_client.get(reverse('notes'))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0

    def test_filter_note_by_tag(self):
        api_client, user_id = create_user('Penny')

        note = create_notes(user_id, "Test Note", "Hello this is my First Note", True,
                            [{"title": "blog"}, {"title": "thoughts"}])

        url = reverse_querystring('note', args=[note.id],
                                  query_kwargs={'tag': 'blog'})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) != 1

