from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  location = models.CharField(max_length=64)

  def __str__(self):
    return self.user.username

class Event(models.Model):
  name = models.TextField()
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

class UserEvent(models.Model):
  userid = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
  eventid = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='users')

  def __str__(self):
    return '{}, {}'.format(self.userid, self.eventid)

class UserCategory(models.Model):
  userid = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
  categoryid = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="users")

  def __str__(self):
    return '{}, {}'.format(self.userid, self.categoryid)

class EventCategory(models.Model):
  eventid = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='categories')
  categoryid = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')

  def __str__(self):
    return '{}, {}'.format(self.eventid, self.categoryid)









