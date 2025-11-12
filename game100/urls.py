"""
URL configuration for game100 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from home.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', new_game),
    path('new_game/', new_game),
    path('game/<str:session_id>/', game_session, name='game_session'),
    path('game/<str:session_id>/next/', game_next_turn, name='game_next_turn'),
    path('game/<str:session_id>/start_turn/', start_player_turn, name='start_player_turn'),
    path('game/<str:session_id>/player/<str:player_id>/', player_turn, name='player_turn'),
    path('game/<str:session_id>/player/<str:player_id>/submit/', submit_result, name='submit_result'),
    path('join_game/', new_player, name='new_player'),
    path('game/<str:session_id>/status/', game_status, name='game_status'),
]
