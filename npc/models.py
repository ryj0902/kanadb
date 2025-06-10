from django.db import models


class Npc(models.Model):
    id = models.IntegerField(primary_key=True)
    chapter_name = models.TextField()
    chapter_name_us = models.TextField()
    loading_name = models.TextField()
    loading_name_us = models.TextField()
    loading_desc = models.TextField()
    loading_desc_us = models.TextField()
    setup = models.TextField()
