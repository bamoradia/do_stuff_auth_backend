
from .models import User, Event, Category, UserEvent, UserCategory, EventCategory
from rest_framework import serializers


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
    	model = Event
    	fields = ('id', 'name', 'date', 'time', 'description', 'url',)