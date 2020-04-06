# Secured system to transfer files and URL addresses

## Features
- User can login, and logout.
- Only logged in user can save new secured resource. If you are not logged in, you will be redirected to login page.
- When form is submitted, be redirected to `/GetResult/<id>` to get URL and password generated to get the secured resource.
- Using the generated open URL (can be opened in a different browser as login is not required) to enter the generated password for the URL to get the secured resource.
- User Agent header of logged in user's last request saved in `User Statistics` in user model inside Django admin. This is created automatically when new user is created either from command line or admin panel).
- All generated links are checked periodically every 60 seconds for expiry. The links are valid for 24 hours, after that they are expired.
- Changing password for a particular element using admin panel.

### REST API
- `/api/token-auth/` - Securing endpoint for registerd users. The body takes a username and password of the user in application JSON. Returns an authorization token which then its used for future secured API endpoints by including it as `Authorization` header with prefix `token` before value obtained.

	```
  	{
		"username": "username",
		"password": "password"
  	}
	```
	Response:
	```
	{
		"token": "<str:token>"
	}
	```

- `/SecuredResource/` - Secured endpoint for adding new elements. The file data can be set from Type option. Type 1 being a URL and Type 2 a file. Post data should be form-data!
	
	```
	{
		"Type": 1,
		"URL": "http://google.com",
		"File": ""
	}
	OR
	{
		"Type": 2,
		"URL": "",
		"File": <filedata>
	}
	```
	Response:
	```
	{
		"url": "<str:UID>",
		"password": "W26KVAFBPC"
	}
	```

- `/data/<str:UID>/` - Open endpoint to get a particular secured resource on generated URL with form data.
  
  	```
	{
  		"password": "W26KVAFBPC"
	}
	```

- `/GetStat` - Secured endpoint to get statistics on the number of items of each type, added everyday, that have been visited or not visited.

  	```
	{
		"2020-04-05": {
			"Files": 3,
			"URLS": 7,
			"UnvisitedFiles": 2,
			"UnvisitedURLs": 4
		},
		"2020-04-06": {
			"Files": 1,
			"URLS": 0,
			"UnvisitedFiles": 0,
			"UnvisitedURLs": 0
		}
	}
	```

## Instructions
- `git clone https://github.com/abedinski/securedproj.git`.
- cd to project folder.
- `docker-compose up -d --build` - Docker all set.
- Update `settings.py` to reflect database`.
- Migrate database `docker-compose exec web python manage.py migrate`.
- `docker-compose exec web python manage.py createsuperuser` since the app requires using the admin.
- http://127.0.0.1:8000/admin is accessible and homepage via login.
- Once finished - `docker-compose down`

## Tests
- `python manage.py test`

## Requirements
- Django
- djangorestframework
- django-crispy-forms
- dj-database-url
- psycopg2-binary
- gunicorn
- whitenoise
