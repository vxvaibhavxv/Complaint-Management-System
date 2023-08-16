# Complaint-Management-System

A Complaint Management System built using Python and Django (Indian Oil Corporation Limited (IOCL) internship project)

## How to setup?
1. Install `Python 3.8.9`
2. Run `pip install virtualenv`
3. Create a virtual environment using `virtualenv environment`
4. Activate the virtual environment using `environment\Scripts\activate`. This will only work for Windows.
5. Install the dependencies using `pip install -r requirements.txt`

## How to run the project?
1. First, create some database migrations using `python manage.py makemigrations core managers` and then migrate them using `python manage.py migrate`
2. Create a superuser using the following `python manage.py createsuperuser` and fill the required details.
3. Admin panel can be accessed at this URL - `http://127.0.0.1:8000/admin/`
4. Run the server using `python manage.py runserver`
