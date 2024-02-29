# PrimBrainLnc
A database for brain lncRNAs from human and non-human primates

## How to get the database?
git clone https://github.com/NavandarM/PrimBrainLnc.git 

## Prerequisite
```bash
sudo apt-get update
sudo apt install python3-virtualenv
python3 -m venv myvirtual
source myvirtual/bin/activate
pip install django
pip install -r requirements.txt  #[ "requirements.txt" is given along with the database and contains dependencies. ]
sudo apt-get install python3-tk 
```
## How to run the server?
python manage.py runserver 0.0.0.0:8000 

## Details of the directories and files:

Project Directory (PrimeOrthoLnc):

- This is the main directory containing the entire Django project.
subdirectories:
  - manage.py: A command-line utility allows to interact with Django project. Use it to run and update the database server.
  - settings.py: This file contains configuration settings of PrimOrthoLnc
  - urls.py: This file contains URL patterns of this project. this file allows to mapping URL paths to views.
  - wsgi.py and asgi.py: These files are entry points for WSGI (Web Server Gateway Interface) and ASGI (Asynchronous Server Gateway Interface) servers respectively.
    
App Directories:

 encapsulate specific functionality.
Each app typically has its own directory within the project.
Each app directory contains various files and subdirectories, including:
models.py: This file defines the data models for the app. It typically contains Python classes that subclass django.db.models.Model.
views.py: This file contains view functions or classes that handle HTTP requests and return HTTP responses.
urls.py: Each app may have its own URL configuration to handle requests specific to that app.
forms.py: If your app requires any custom forms, they are typically defined in this file.
admin.py: This file is used to register models with the Django admin interface for managing data via the admin site.
tests.py: This file contains unit tests for testing the functionality of the app.
migrations/: This directory contains database migrations created for the app. Migrations are used to propagate changes made to models into the database schema.
static/: This directory is used to store static files (e.g., CSS, JavaScript, images) specific to the app.
templates/: This directory contains HTML templates used to render views for the app.
Static Files:

In addition to app-specific static files, Django projects typically have a global static/ directory at the project level to store static files shared across multiple apps.
Templates:

Similar to static files, Django projects often have a global templates
