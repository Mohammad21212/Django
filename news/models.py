from django.db import models

class News(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    tag = models.CharField(max_length=50)
    source = models.CharField(max_length=255)

    def __str__(self):
        return self.title
