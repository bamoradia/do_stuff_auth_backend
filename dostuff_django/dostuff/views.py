from django.shortcuts import render
from django.http import JsonResponse
from .models import Event, Category, UserEvent, UserCategory, EventCategory

from rest_framework import generics
from .serializers import EventSerializer
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json

# Create your views here.

# class EventList(generics.ListCreateAPIView):
# 	queryset = Event.objects.all()
# 	serializer_class = EventSerializer

# class EventDetail(generics.RetrieveUpdateDestroyAPIView):
# 	queryset = Event.objects.all()
# 	serializer_class = EventSerializer
	

def events_list(request):
	events = Event.objects.all()
	events_serialized = serializers.serialize('json', events)

	# events = Event.objects.all()
	# serializer_class = EventSerializer
	return JsonResponse(events_serialized, safe=False)

@csrf_exempt
def user_add_event(request):
	if request.method == 'POST':
		event = Event.objects.get(pk=1) # change 1 to variable that holds userid --> sent in request
		# event_serialized = serializers.serialize('json', [event, ])

		user = User.objects.get(pk=1) # change 1 to variable that holds userid --> sent in request

		user_event = UserEvent(userid=user, eventid=event)
		user_event.save()

		return JsonResponse({'status': 'Added Event to User'})

@csrf_exempt
def user_delete_event(request):
	if request.method == 'DELETE':
		event = Event.objects.get(pk=1)

		user = User.objects.get(pk=1)

		user_event = UserEvent.objects.get(userid=1, eventid=1)

		user_event.delete()

		return JsonResponse({'status': 'Removed Event from User'})



@csrf_exempt
def create_user(request):
	if request.method == 'POST':

		user = User.objects.create(username='freddie')
		user.set_password('iHateCoding')

		user.save()
		

		return JsonResponse({'status': 'added user'})


@csrf_exempt
def testing(request):
	if request.method == 'POST':

		# body_unicode = request.body.decode('utf-8')
		
		print(request.POST['test'], 'this is the request.body')		

		return JsonResponse({'status': 'added user'})




