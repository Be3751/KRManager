from django.urls import path
from . import views

urlpatterns = [
    # /auth: 認証ページにリダイレクト
    # /auth/complete: 認証完了
    path('', views.index, name='zoom_index'),
    path('auth/', views.auth, name='zoom_auth'),
    path('auth/complete', views.auth_complete, name='zoom_auth_complete'),
]