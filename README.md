[![Build Status](https://travis-ci.com/abedinski/securedproj.svg?branch=master)](https://travis-ci.com/abedinski/securedproj)

# Secured system to transfer files and URL addresses

## Features
- User can login, and logout.
- Only logged in user can save new secured resource. If you are not logged in, you will be redirected to login page.
- When a form is submitted, be redirected to `/get_result/<id>` to get url and password generated to get the secured resource.
- Using the generated open url (can be opened in a different browser as login is not required) to enter the generated password for the url to get the secured resource.
- User agent header of logged in user's last request saved in `User Statistics` in user model inside Django admin. This is created automatically when new user is created either from command line or admin panel).
- All generated links are checked periodically every 60 seconds for expiry. The links are valid for 24 hours, after that they are expired.
- Changing password for a particular element using admin panel.

### REST API
- `/api/token-auth` - Securing endpoint for registerd users. The body takes a username and password of the user in application JSON. Returns an authorization token which then its used for future secured API endpoints by including it as `Authorization` header with prefix `token` before value obtained.

	```
  	{
		"username": "username",
		"password": "password"
  	}
	```
	Response
	```
	{
		"token": "<str:token>"
	}
	```

- `/api/secured_resource` - Secured endpoint for adding new elements. The file data can be set from `res_type` option. `res_type 1`  being a url and `res_type 2` a file. Post data should be form-data.
	
	```
	{
		"res_type": 1,
		"url": "http://google.com"
	}
	```
	or
	```
	{
		"res_type": 2,
		"res_file": <filedata>
	}
	```
	Response
	```
	{
		"url": "<str:url>",
		"password": "<str:password>"
	}
	```

- `/api/data/<str:uid>` - Open endpoint to get a particular secured resource on generated url with form data.
  
  	```
	{
  		"password": "<str:password>"
	}
	```
	Response: If its a file, will return a file response otherwise a link to the secured url.
	```
	{
		"url": "<str:url>"
	}

- `/api/get_stat` - Secured endpoint to get statistics on the number of items of each type, added everyday, that have been visited or not visited.

  	```
	{
		"2020-04-05": {
			"files": 3,
			"urls": 7,
			"unvisited_files": 2,
			"unvisited_urls": 4
		},
		"2020-04-06": {
			"files": 1,
			"urls": 0,
			"unvisited_files": 0,
			"unvisited_urls": 0
		}
	}
	```

## Instructions
- `git clone https://github.com/abedinski/securedproj.git`.
- cd to project folder.
- `docker-compose up -d --build` - Docker all set.
- Update `settings.py` to reflect database`.
- Migrate `docker-compose exec web python manage.py migrate`.
- Create a super user `docker-compose exec web python manage.py createsuperuser` since the app requires using the admin.
- http://127.0.0.1:8000/admin is accessible and homepage via login.
- Once finished `docker-compose down`.

## Tests
- `docker-compose run web python manage.py test`

## Requirements
- Django
- djangorestframework
- django-crispy-forms
- dj-database-url
- psycopg2-binary
- gunicorn
- whitenoise
