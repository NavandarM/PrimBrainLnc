# PrimBrainLnc
A database of brain lncRNAs from human and non-human primates multiple brain regions.
link: http://primbrainlnc.bio.uni-mainz.de/

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

__Project Directory (PrimeOrthoLnc):__

- This is the main directory containing the entire Django project.
  
subdirectories:
  - manage.py: A command-line utility allows to interact with Django project. Use it to run and update the database server.
  - settings.py: This file contains configuration settings of PrimOrthoLnc
  - urls.py: This file contains URL patterns of this project. this file allows to mapping URL paths to views.
  - wsgi.py and asgi.py: These files are entry points for WSGI (Web Server Gateway Interface) and ASGI (Asynchronous Server Gateway Interface) servers respectively.
    
__App Directory (Application):__

 - Provides separate files for different task i.e. encapsulate specific functionality.

Files and directories:
  - models.py: This file defines the data models/schema for the application.
  - views.py: This file contains view functions or classes that handle HTTP requests and return HTTP responses.
  - urls.py:  This file informs the application how to respond to different web page requests and connect them to specific views or functions.
  - forms.py: It allows to desigb the custom forms of the web page.
  - admin.py: This file is used to register models with the Django admin interface for managing data via the admin site.
  - tests.py: This file contains unit tests for testing the functionality of the app.
  - migrations/: This directory contains database migrations created for the app. Migrations are used to propagate changes made to models into the database schema.

__static/:__

- This directory is used to store static files (e.g., CSS, JavaScript, images, software, temporary files generated ).

__templates/:__

- This directory contains HTML templates used to render views for the app.

__population_script.py__

- To populate the PrimOrthoLnc database with the dataset.
- Dataset file:__Input_for_database_GeneralInfo_sequenceupdated.txt__
