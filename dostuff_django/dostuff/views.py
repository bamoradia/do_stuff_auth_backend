from django.shortcuts import render
from django.http import JsonResponse, QueryDict
from django.contrib.auth.models import User
from .models import Event, Category, UserEvent, UserCategory, EventCategory, UserProfile
from rest_framework import generics
from .serializers import EventSerializer
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import requests
import time
import datetime
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# Create your views here.

# class EventList(generics.ListCreateAPIView):
# 	queryset = Event.objects.all()
# 	serializer_class = EventSerializer

# class EventDetail(generics.RetrieveUpdateDestroyAPIView):
# 	queryset = Event.objects.all()
# 	serializer_class = EventSerializer
@csrf_exempt
def not_logged_in(request):
	return JsonResponse({'status': 400, 'data': 'User not authenitcated'})


@csrf_exempt
def log_user_in(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
    	# print(request, user)
    	login(request, user)
    	return JsonResponse({'status': 200, 'data': 'LOGGED IN'})
    else:
    	return JsonResponse({'status': 400, 'data': 'Did not Log in'})



@csrf_exempt
@login_required
def logout_view(request):
    logout(request)
    return JsonResponse({'status': 200, 'data': 'Logged Out'})
	


# SEND BACK ALL EVENTS IF NOT LOGGED IN AND ALL CATEGORIES
# SEND BACK USER EVENTS AND CATEGORIES IF LOGGED IN
def events_list(request):
	events = Event.objects.all()
	categories = Category.objects.all()

	# Need to find user's location for intial event search
	# Need to update date so it only pulls event from today onwards

	current_time = int(time.time())
	next_week = current_time + 604800

	response = requests.get("https://api.yelp.com/v3/events?location=Chicago&limit=50&start_date={}&end_date={}".format(current_time, next_week), headers={'Authorization': 'Bearer gr0amugCLWzgKkSCIgPZnPI8e7cRXFuEprIOGszYzUIo9JH5kWT1LMMZUkIW0tOBpywUrjmxns-zKDh5FoGsj4_SPNZG_-WDeGAzOCESd0wG9ZX5tUOXIRo4H2poW3Yx'})

	response_json = response.json()

	in_database = False

	for i in range(0, len(response_json['events'])):
		for j in range(0, len(events)):
			if events[j].url == response_json['events'][i]['event_site_url']:
				in_database = True

		if in_database == False:
			#add event to database
			date_str, time_str = response_json['events'][i]['time_start'].split(' ')
			year, month, day = date_str.split('-')

			s = '{}/{}/{}'.format(day, month, year)

			unix_time = time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())

			e = Event(name=response_json['events'][i]['name'], date=unix_time, time=time_str, description=response_json['events'][i]['description'], url=response_json['events'][i]['event_site_url'])

			e.save()

			for k in range(0, len(categories)):
				if(categories[k].name == response_json['events'][i]['category']):
					ec = EventCategory(eventid=e, categoryid=categories[k])
					ec.save()



			# also need to find category and search database for category match then add to eventcategory table
			in_database = False

	new_event_list = Event.objects.all()
	events_serialized = serializers.serialize('json', new_event_list)

	category_list = Category.objects.all()
	categories_serialized = serializers.serialize('json', category_list)
	
	# response.json()
	# response_json = serializers.serialize('json', response)

	# events = Event.objects.all()
	# serializer_class = EventSerializer
	return JsonResponse({'status': 200, 'data': {'events': events_serialized, 'categories': categories_serialized}})




# NO DATA NEEDED IN RESPONSE
@csrf_exempt
@login_required
def user_add_event(request):
	if request.method == 'POST':
		event = Event.objects.get(pk=request.POST['eventid']) # change 1 to variable that holds userid --> sent in request
		# event_serialized = serializers.serialize('json', [event, ])

		user = User.objects.get(pk=request.POST['userid']) # change 1 to variable that holds userid --> sent in request

		user_event = UserEvent(userid=user, eventid=event)
		user_event.save()

		return JsonResponse({'status': 'Added Event to User'})



# NO DATA NEEDED IN RESPONSE
@csrf_exempt
@login_required(redirect_field_name='not_logged_in')
def user_delete_event(request):
	if request.method == 'DELETE':
		event = Event.objects.get(pk=request.POST['eventid'])

		user = User.objects.get(pk=request.POST['userid'])

		user_event = UserEvent.objects.get(userid=request.POST['userid'], eventid=request.POST['eventid'])

		user_event.delete()

		return JsonResponse({'status': 'Removed Event from User'})




# USERID AND LOGGED IN TRUE 
@csrf_exempt
def create_user(request):
	if request.method == 'POST':
		user = User.objects.create(username=request.POST['username'])
		user.set_password(request.POST['password'])

		user.save()

		user_profile = UserProfile(user=user, location=request.POST['location'])
		user_profile.save()

		return JsonResponse({'status': 200, 'userid': user.id})





# UPDATED LIST OF ALL USER CATEGORY EVENTS
@csrf_exempt
@login_required(login_url='/api/authentication-error')
def edit_user(request):
	if request.method == 'PUT':
		# request.POST['userid']
		request_dict = QueryDict(request.body).dict()

		user_match = User.objects.get(pk=request_dict['userid'])
		user_profile = UserProfile.objects.get(user=user_match)

		user_profile.location = request_dict['location']
		user_profile.save()

		categories = UserCategory.objects.filter(userid=request_dict['userid'])

		categories.delete()

		cat_list = eval(request_dict['category'])

		user_events = []

		for i in range(0, len(cat_list)):
			category_model = Category.objects.get(name=cat_list[i])
			user_category = UserCategory(userid=user_match, categoryid = category_model)
			user_category.save()


		user_cats = UserCategory.objects.filter(userid=request_dict['userid'])

		for i in range(0, len(user_cats)):
			cat_events = EventCategory.objects.filter(categoryid=user_cats[i].categoryid)
			user_events.extend(cat_events)

		events = []

		for i in range(0, len(user_events)):
			print(user_events[i].eventid,'this the user event')
			# found_event = Event.objects.get(id=user_events[i].eventid)
			events.append(user_events[i].eventid)




		events_serialized = serializers.serialize('json', events)
		#FIND ALL CATEGORIES ASSOCIATED WITH USER
		#FIND ALL EVENTS ASSOCIATED WITH THOSE CATEGORIES


		return JsonResponse({'status': 200, 'data': events_serialized})




# REMOVE LOGGED IN TRUE
@csrf_exempt
@login_required
def delete_user(request):
	if request.method == 'DELETE':

		request_dict = QueryDict(request.body).dict()
		user_match = User.objects.get(pk=request_dict['userid'])
		user_match.delete()	

		return JsonResponse({'status': 'deleted user'})




# CONFIRMATON THAT CATEGORIES WERE ADDED
@csrf_exempt 
# Just used to initially load categories into database
def populate_categories(request):
	categories=['music', 'food-and-drink', 'other', 'performing-arts', 'charities', 'festivals-fairs', 'sports-active-life', 'nightlife', 'visual-arts', 'kids-family', 'fashion', 'film', 'lectures-books']

	database_categories = Category.objects.all()
	database_categories.delete()

	for i in range(0, len(categories)):
		c = Category(name=categories[i])
		c.save()

	return JsonResponse({'status': 'Created Categories'})


@csrf_exempt 
def testing(request):
	print(request.user.is_authenticated)


	return JsonResponse({'status': 200})


