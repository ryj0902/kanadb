from django.db import models


class Deck(models.Model):
    id = models.IntegerField(primary_key=True)
    chapter_name = models.CharField(max_length=40)
    chapter_name_us = models.CharField(max_length=40)
    loading_name = models.CharField(max_length=40)
    loading_name_us = models.CharField(max_length=40)
    loading_desc = models.TextField()
    loading_desc_us = models.TextField()
    setup = models.TextField()
