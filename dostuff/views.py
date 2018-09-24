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
import secrets
from twilio.rest import Client
import threading


# Your Account SID from twilio.com/console
account_sid = "ACfbf02ec44aa05b5acc501fd124f4ef4c"
# Your Auth Token from twilio.com/console
auth_token  = "80c548e33b468c16cbf85258d7815e10"
client = Client(account_sid, auth_token)


@csrf_exempt
def not_logged_in(request):
	return JsonResponse({'status': 400, 'data': 'User not authenitcated'})


@csrf_exempt
def log_user_in(request):


	parsed_data = json.loads(request.body)

	username = parsed_data['username']
	password = parsed_data['password']

	user = authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)
		#create a new secret key for this session
		key = secrets.token_hex(55)
		user_match = User.objects.get(username=username)

		#if User is Badal, send a text with authenitcation token via sms
		#using trial account on Twilio -> can only send sms to one number
		if username == 'TestSMS':
			auth_token = secrets.token_hex(3)

			message = client.messages.create(
		    to="+16306870821", 
		    from_="+16282227315",
		    body=auth_token)


		#update the user_profile with the new key
		user_profile = UserProfile.objects.get(user=user_match)
		user_profile.key = key
		user_profile.last_login = time.time()
		user_profile.save()
		#find all categories the user has saved
		user_categories = UserCategory.objects.filter(userid=user)
		categories = []
		#loop over the categories to get in more friendly way
		for i in range(0, len(user_categories)):
			# cat = Category.objects.get(pk=user_categories[i].categoryid)
			categories.append(user_categories[i].categoryid)
		user_categories_JSON = serializers.serialize('json', categories)

		user_events_queryset = UserEvent.objects.filter(userid=user_match)

		user_events = []
		for i in range(0, len(user_events_queryset)):

			if int(time.time()) < user_events_queryset[i].eventid.date:
				user_events.append(user_events_queryset[i].eventid)


		user_events_serialized = serializers.serialize('json', user_events)
		return JsonResponse({'status': 200, 'userid': user_match.id, 'categories': user_categories_JSON, 'key': key, 'location': user_profile.location, 'events': user_events_serialized})
	else:
		return JsonResponse({'status': 400, 'data': 'Did not Log in'})



@csrf_exempt
def logout_view(request):
	parsed_data = json.loads(request.body)
	#check if user exists in database
	user_check = User.objects.filter(pk=parsed_data['userid'])
	if user_check: 
		user_match = User.objects.get(pk=parsed_data['userid'])
		user_profile = UserProfile.objects.get(user=user_match)
	#if user exists, key matches and user is authenticated, logout user
	if request.user.is_authenticated and user_check and parsed_data['key'] == user_profile.key :
	    logout(request)
	    user_profile.key = secrets.token_hex(55)
	    user_profile.save()
	    return JsonResponse({'status': 200, 'data': 'Logged Out'})
	else: 
		return JsonResponse({'status': 400, 'data': 'User not authenticated'})
	


# SEND BACK ALL EVENTS IF NOT LOGGED IN AND ALL CATEGORIES
# SEND BACK USER EVENTS AND CATEGORIES IF LOGGED IN
def events_list(request):
	events = Event.objects.all()
	categories = Category.objects.all()

	# Need to find user's location for intial event search
	# Need to update date so it only pulls event from today onwards

	current_time = int(time.time())
	next_week = current_time + 604800

	response = requests.get("https://api.yelp.com/v3/events?location=Chicago&limit=50&start_date={}".format(current_time), headers={'Authorization': 'Bearer gr0amugCLWzgKkSCIgPZnPI8e7cRXFuEprIOGszYzUIo9JH5kWT1LMMZUkIW0tOBpywUrjmxns-zKDh5FoGsj4_SPNZG_-WDeGAzOCESd0wG9ZX5tUOXIRo4H2poW3Yx'})

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

			e = Event(
				name=response_json['events'][i]['name'], 
				date=unix_time, time=time_str, 
				description=response_json['events'][i]['description'], 
				url=response_json['events'][i]['event_site_url'], 
				category=response_json['events'][i]['category'],
				image_url=response_json['events'][i]['image_url'],
				address=response_json['events'][i]['location']['address1'],
				city=response_json['events'][i]['location']['city'],
				state=response_json['events'][i]['location']['state']
			)

			e.save()

			for k in range(0, len(categories)):
				if(categories[k].name == response_json['events'][i]['category']):
					ec = EventCategory(eventid=e, categoryid=categories[k])
					ec.save()



			# also need to find category and search database for category match then add to eventcategory table
		in_database = False

	new_event_list = Event.objects.all()
	events_list = []
	count = 0
	for i in range(0, len(new_event_list)):
		if int(time.time()) < new_event_list[i].date:
				events_list.append(new_event_list[i])
				count += 1
	events_serialized = serializers.serialize('json', events_list)

	category_list = Category.objects.all()
	categories_serialized = serializers.serialize('json', category_list)
	
	# response.json()
	# response_json = serializers.serialize('json', response)

	# events = Event.objects.all()
	# serializer_class = EventSerializer
	return JsonResponse({'status': 200, 'data': {'events': events_serialized, 'categories': categories_serialized}})




# NO DATA NEEDED IN RESPONSE
@csrf_exempt
def user_add_event(request):
	parsed_data = json.loads(request.body)
	user_check = User.objects.filter(pk=parsed_data['userid'])
	if user_check: 
		user_match = User.objects.get(pk=parsed_data['userid'])
		user_profile = UserProfile.objects.get(user=user_match)

	if request.method == 'POST' and user_check and user_profile.key == parsed_data['key']:
		event = Event.objects.get(url=parsed_data['event']) # change 1 to variable that holds userid --> sent in request
		# event_serialized = serializers.serialize('json', [event, ])

		event_exists = UserEvent.objects.filter(userid=user_match, eventid=event).exists()
		if event_exists:
			return JsonResponse({'status': 204, 'data': 'Event already in User DB'})
		else: 
			user_event = UserEvent(userid=user_match, eventid=event)
			user_event.save()

			return JsonResponse({'status': 200, 'data': 'Added Event to User'})
	else: 
		return JsonResponse({'status': 401, 'data': 'User not authenticated'})



# NO DATA NEEDED IN RESPONSE
@csrf_exempt
def user_delete_event(request):
	parsed_data = json.loads(request.body)
	user_check = User.objects.filter(pk=parsed_data['userid'])
	if user_check: 
		user_match = User.objects.get(pk=parsed_data['userid'])
		user_profile = UserProfile.objects.get(user=user_match)

	if request.method == 'POST' and user_check and user_profile.key == parsed_data['key']:
		event = Event.objects.get(url=parsed_data['event']) # change 1 to variable that holds userid --> sent in request
		# event_serialized = serializers.serialize('json', [event, ])

		event_exists = UserEvent.objects.filter(userid=user_match, eventid=event).exists()
		if not event_exists:
			return JsonResponse({'status': 204, 'data': 'Event not in user events database'})
		else: 
			user_event = UserEvent.objects.get(userid=user_match, eventid=event)
			user_event.delete()

			return JsonResponse({'status': 200, 'data': 'Added Event to User'})
	else: 
		return JsonResponse({'status': 401, 'data': 'User not authenticated'})




# USERID AND LOGGED IN TRUE 
@csrf_exempt
def create_user(request):
	if request.method == 'POST':

		parsed_data = json.loads(request.body)

		# Search if username is already in database
		userExists = User.objects.filter(username=parsed_data['username']).exists()

		if userExists: 
			return JsonResponse({'status': 403, 'message': 'Username already exists'})
		else: 
			user = User.objects.create(username=parsed_data['username'])
			user.set_password(parsed_data['password'])

			user.save()

			user_profile = UserProfile(user=user, location=parsed_data['location'])
			user_profile.save()


			return JsonResponse({'status': 200, 'userid': user.id})





# UPDATED LIST OF ALL USER CATEGORY EVENTS
@csrf_exempt
def edit_user(request):
	if request.method == 'PUT':
		request_dict = json.loads(request.body)
		#check if user exists with given user ID
		userExists = User.objects.filter(pk=request_dict['userid']).exists()
		#if user exists, then find the user and user profile
		if userExists:
			user_match = User.objects.get(pk=request_dict['userid'])
			user_profile = UserProfile.objects.get(user=user_match)
			#check if key matches user key
			if user_profile.key == request_dict['key']:

				user_profile.location = request_dict['location']
				user_profile.save()

				categories_check = UserCategory.objects.filter(userid=user_match).exists()

				if categories_check: 
					categories = UserCategory.objects.filter(userid=user_match)
					categories.delete()

				# cat_list = eval(request_dict['categories'])
				cat_list = request_dict['categories']
				print(cat_list, 'this is the categories list from React')

				user_events = []

				for i in range(0, len(cat_list)):
					category_model = Category.objects.get(name=cat_list[i])
					user_category = UserCategory(userid=user_match, categoryid = category_model)
					print(user_category, 'THIS IS USER CATEGORY')
					user_category.save()


				user_cats = UserCategory.objects.filter(userid=request_dict['userid'])

				for i in range(0, len(user_cats)):
					cat_events = EventCategory.objects.filter(categoryid=user_cats[i].categoryid)
					user_events.extend(cat_events)

				events = []

				for i in range(0, len(user_events)):
					# found_event = Event.objects.get(id=user_events[i].eventid)
					events.append(user_events[i].eventid)

				events_serialized = serializers.serialize('json', events)
				#FIND ALL CATEGORIES ASSOCIATED WITH USER
				#FIND ALL EVENTS ASSOCIATED WITH THOSE CATEGORIES


				return JsonResponse({'status': 200, 'data': events_serialized})
			else: 
				return JsonResponse({'status': 400, 'data': 'User not authenticated'})
		else: 
			return JsonResponse({'status': 400, 'data': 'User not authenticated'})
	else: 
		return JsonResponse({'status': 400, 'data': 'User not authenticated'})




# REMOVE LOGGED IN TRUE
@csrf_exempt
def delete_user(request):
	if request.method == 'DELETE' and request.user.is_authenticated:

		request_dict = QueryDict(request.body).dict()
		user_match = User.objects.get(pk=request_dict['userid'])
		user_match.delete()	

		return JsonResponse({'status': 'deleted user'})
	else: 
		return JsonResponse({'status': 400, 'data': 'User not authenticated'})




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

	if request.user.is_authenticated:
		print(request.user)
		return JsonResponse({'status': 200, 'data': request.user})
	else: 
		return JsonResponse({'status': 400, 'data': 'user was not logged in'})




test_count = 0
def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec) 
        func()  
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def test_function():
	print('test')



set_interval(test_function, 540)







