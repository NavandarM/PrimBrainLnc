# PrimBrainLnc
A database for brain lncRNAs from human and non-human primates

## How to get the database?
git clone https://github.com/NavandarM/PrimBrainLnc.git

## Prerequisite
sudo apt-get update
sudo apt install python3-virtualenv
python3 -m venv myvirtual
pip install django
source myvirtual/bin/activate
pip install -r requirements.txt  [ "requirements.txt" is given along with the database and contains dependencies. ]
sudo apt-get install python3-tk

## How to run server?
python manage.py runserver 0.0.0.0:8000
