from django.db import models

class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    last_synced = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username
    
class Film(models.Model):
    film_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    poster_image = models.CharField(max_length=500, null=True, blank =True)
    genres = models.JSONField(default=list)

    def __str__(self):
        return self.title
    
class WatchlistEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'film')

    def __str__(self):
        return f'{self.user.username} - {self.film.title}'
