from django.db import models

# Create your models here.

class User(models.Model):
  username = models.CharField(max_length=32)
  password = models.CharField(max_length=32)
  location = models.CharField(max_length=64)

  def __str__(self):
    return self.name

class Event(models.Model):
  name = models.CharField(max_length=100)
  date = models.IntegerField()
  time = models.CharField(max_length=32)
  description = models.TextField()
  url = models.TextField()

  def __str__(self):
    return self.name

class Category(models.Model):
  name = models.CharField(max_length=32)

  def __str__(self):
    return self.name