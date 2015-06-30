from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers
from imdb import views

router = routers.DefaultRouter()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'payal.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^add_movie?(?:$|\/$)', views.add_movie),
	url(r'^edit_movie?(?:$|\/$)', views.edit_movie),
	url(r'^delete_movie?(?:$|\/$)', views.delete_movie),
	url(r'^search?(?:$|\/$)', views.search),
	url(r'^get_movies?(?:$|\/$)', views.get_movies),
	url(r'^signup_user?(?:$|\/$)', views.signup_user),
    url(r'^login_user?(?:$|\/$)', views.login)
)

