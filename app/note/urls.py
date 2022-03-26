# -*- coding: utf-8 -*-

from django.urls import path, re_path

from note import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='auth_register'),
    path('user/', views.UsersAPIView.as_view(), name='users'),
    re_path(r'user/(?P<user_id>[^/]+)$', views.UserAPIView.as_view(), name='user'),
    path('notes/', views.NotesView.as_view(), name='notes'),
    re_path(r'note/(?P<id>[^/]+)$', views.NoteView.as_view(), name='note'),
]
