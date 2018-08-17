from django.shortcuts import render
from django.http import JsonResponse
from .models import User, Event, Category, UserEvent, UserCategory, EventCategory

from rest_framework import generics
from .serializers import EventSerializer

# Create your views here.

class EventList(generics.ListCreateAPIView):
	queryset = Event.objects.all()
	serializer_class = EventSerializer

class EventDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Event.objects.all()
	serializer_class = EventSerializer
	


