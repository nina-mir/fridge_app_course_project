"""Fridge_9000 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf.urls import include
from refrigerator_app import views
from recipes import views as recipe_views
from django.contrib.auth import views as auth_views
from users import views as user_views
from refrigerator_app import fridge as fridge_manager

urlpatterns = [
    path('', views.home, name='home'),
    path('fridge/check/', fridge_manager.initialCurrentFridge, name='fridge_init'),
    path('fridge/', views.fridge, name='fridge'),
    path('add/', views.add_button, name='add_button'),
    path('groceries/', views.groceries, name='groceries'),
    path('recipes/', recipe_views.recipe_landing, name='recipes'),
    path('recipes/search/', recipe_views.recipe_search, name='recipe_search'),
    path('recipes/search', recipe_views.recipe_search_results,
         name='recipe_search_results'),
    path('profile/', views.profile, name='profile'),
    # path('upload/', views.receipt_upload, name='upload'),
    path('auth/register/', user_views.register, name='register'),
    path('auth/login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('auth/logout/', auth_views.LogoutView.as_view(
        template_name='users/logout.html'), name='logout'),
    path('admin/', admin.site.urls),
    path('search/', views.search, name='search')
]
