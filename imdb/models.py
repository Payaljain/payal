from django.db import models

# Create your models here.
class Genre(models.Model):

	class Meta:
		db_table = 'genre'

	name = models.CharField(max_length = 128)


class Movies(models.Model):

	class Meta:
		db_table = 'movies'

	director = models.CharField(max_length = 128)
	name = models.CharField(max_length = 512)
	popularity = models.DecimalField(max_digits = 3, decimal_places = 1, default=0.0)
	score = models.DecimalField(max_digits = 2, decimal_places = 1, default = 0.0)
	genres = models.ManyToManyField(Genre)

