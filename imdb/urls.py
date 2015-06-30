from django.conf.urls import patterns, url
from imdb.views import *
from rest_framework.authtoken import views

from rest_framework import routers
from . import views

router = routers.DefaultRouter()
urlpatterns = patterns(
	router.register(r'^add_movie?(?:$|\/$)', add_movie),
	router.register(r'^edit_movie?(?:$|\/$)', edit_movie),
	router.register(r'^delete_movie?(?:$|\/$)', delete_movie),
	router.register(r'^search?(?:$|\/$)', search),
	router.register(r'^get_movies?(?:$|\/$)', get_movies),
	router.register(r'^signup_user?(?:$|\/$)', signup_user),

	router.register(r'^login_user?(?:$|\/$)', views.login)
)