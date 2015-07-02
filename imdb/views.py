from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Movies,Genre
from django.db.models import Q
from django.contrib.auth import authenticate, login
import json
import sys


ITEMS_PER_PAGE = 10

# Create your views here.

@api_view(['POST'])
def add_movie(request,format= None):

	if request.user.is_superuser:
		name = request.POST['name']
		genres = request.POST['genres']
		director = request.POST['director']

		movie = model.Movies(name = name, director = director)
		movie.save()

		genres = json.loads(genres)

		for genre in genres:
			genre_obj, created = Genre.objects.get_or_create(name = genre)

			movie.genres.add(genre_obj)

		movie_details = get_movie_details(movie)

		es.index(index = 'imdb', doc_type = 'movies', body = movie_details)

		return Response(movie_details)
	
	return Response('Not allowed to add movies')



@api_view(['POST'])
def edit_movie(request):
	if request.user.is_superuser:
		movie_id = request.POST['id']

		try:
			movie = Movies.objects.get(pk = movie_id)
		except:
			return Response(dict(status = 0, data = 'Invalid ID'))

		id = (es.search(index = 'imdb', q = 'name:"'+movie.name+'"'))['hits']['hits'][0]['_id']
		es.delete(index = 'movies', doc_type = 'movies', id = id)

		if 'name' in request.POST and len(request.POST['director']) == 0:
			name = request.POST['name']

			movie.name = name

		if 'genres' in request.POST:
			genres = json.loads(request.POST['genres'])

			for genre in genres:
				genre_obj, created = Genre.objects.get_or_create(name = genre)

				movie.genres.add(genre_obj)

		if 'director' in request.POST and len(request.POST['director']) == 0:
			director = request.POST['director']
			movie.director = director

		if 'popularity' in request.POST:
			popularity = request.POST['popularity']
			movie.popularity = float(popularity)

		if 'score' in request.POST:
			score = request.POST['score']
			movie.score = float(score)

		movie_details = get_movie_details(movie)

		es.index(index = 'imdb', doc_type = 'movies', body = movie_details)

		return Response(movie_details)
	else:
		return Response('Not allowed to edit movies')


@api_view(['POST'])
def delete_movie(request):
	if request.user.is_superuser:
		movie_id = request.POST['id']
		print >>sys.stderr,movie_id

		try:
			movie = Movies.objects.get(pk = movie_id)
		except:
			return Response(dict(status = 0, data = 'Invalid ID'))

		id = (es.search(index = 'imdb', q = 'name:"'+movie.name+'"'))['hits']['hits'][0]['_id']
		es.delete(index = 'movies', doc_type = 'movies', id = id)

		movie.delete()

		return Response('Success')
	else:
		return Response("Not allowed to delete movies")


def get_movie_details(movie):
	details = {
		'name': movie.name,
		'director': movie.director,
		'genres': [genre_obj.name for genre_obj in movie.genres.all()],
		'popularity': movie.popularity,
		'score': movie.score
	}

	return details


#A search engine like Solr or Elasticsearch would be the ideal way to implement this.
@api_view(['GET'])
def search(request):
	term = request.GET['term']
	page = request.GET.get('page', 0)

	lo = int(page) * ITEMS_PER_PAGE
	hi = (int(page) + 1) * ITEMS_PER_PAGE

	
	terms = term.split()

	matching_movies = Movies.objects.filter(Q(name__contains = term) | Q(director__contains = term) | Q(genres__name__contains = term))
	if len(terms) > 0:
		for term in terms:
			temp = Movies.objects.filter(Q(name__contains = term) | Q(director__contains = term))
			list(matching_movies).extend((temp))

	matching_movies = list(set(matching_movies))

	result = [get_movie_details(movie) for movie in matching_movies][lo : hi]

	return Response(result)


@api_view(['GET'])
def advanced_search(request):
	term = request.GET['term']
	page = request.GET.get('page', 0)

	es = Elasticsearch()

	lo = int(page) * ITEMS_PER_PAGE
	hi = (int(page) + 1) * ITEMS_PER_PAGE

	hits = es.search(index='imdb', q=term, size=1000)

	movies_details = [hit['_source'] for hit in hits['hits']['hits']][lo: hi]

	return Response(movies_details)


def initialize_elasticsearch():
	es = Elasticsearch()

	es.indices.create(index = 'imdb', body = {
		'index.cache.query.enable': True,

		'number_of_shards': 1,

		'number_of_replicas': 0,

		'analysis': {

			'filter': {
				'nGram_filter': {
					'type': 'edgeNGram',
					'min_gram': 3,
					'max_gram': 20,
					'token_chars': ['letter', 'digit']
				},
			},

			'tokenizer': {
				'custom_tokenizer': {
					'type': 'pattern',
					'pattern': '\W+',
				}
			},

			'analyzer': {
				'nGram_analyzer': {
					'type': 'custom',
					'tokenizer': 'custom_tokenizer',
					'filter': ['lowercase', 'asciifolding', 'nGram_filter']
				},

				'whitespace_analyzer': {
					'type': 'custom',
					'tokenizer': 'custom_tokenizer',
					'filter': ['lowercase', 'asciifolding']
				}
			}
		}
	})

	es.indices.put_mapping(index = 'imdb', doc_type = 'movies', body = {
		'movies': {
			'_all': {
				'index_analyzer': 'nGram_analyzer',
				'search_analyzer': 'whitespace_analyzer'
			},

			'properties': {
				'name': {
					'type': 'string',
					'_boost': 1.5,
				},

				'director': {
					'type': 'string',
					'_boost': 1.2,
				},

				'genre': {
					'type': 'string',
				},

				'score': {
					'type': 'float',
					'index': 'no'
				},

				'popularity': {
					'type': 'float',
					'index': 'no'
				}

			},
		}
	})

	movies = Movies.objects.all()

	for movie in movies:
		es.index(index = 'imdb', doc_type = 'movies', body = get_movie_details(movie))


@api_view(['GET'])
def get_movies(request):
	page = request.GET.get('page', 0)

	lo = int(page) * ITEMS_PER_PAGE
	hi = (int(page) + 1) * ITEMS_PER_PAGE

	movies = Movies.objects.all()

	result = [get_movie_details(movie) for movie in movies][lo : hi]

	return Response(result)


@api_view(['POST'])
def signup_user(request):
	first_name = request.POST['first_name']
	last_name = request.POST['last_name']
	password = request.POST['password']
	email = request.POST['email']

	user = User.objects.create_user(first_name, email, password)
	user.last_name = last_name

	user.save()

	token, created = Token.objects.get_or_create(user = user)

	return Response(dict(token = token.key))

@api_view(['POST'])
def login(request):
	username = request.POST['username']
	password = request.POST['password']
	user = auth.authenticate(username = username, password = password)
	if user is not None:
		auth.login(request, user)
		response = Response(reverse('get_movies'))
		return Responseresponse
	else:
		return Response("Couldnot log in")