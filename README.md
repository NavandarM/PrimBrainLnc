# PrimBrainLnc
A database of brain lncRNAs from human and non-human primates multiple brain regions. <br>
Link: http://primbrainlnc.bio.uni-mainz.de/
<br>
Publication: Navandar, M., Vennin, C., Lutz, B., and Gerber, S. Long non-coding RNAs expression and regulation across different brain regions in primates. Sci Data 11, 545 (2024).
(https://doi.org/10.1038/s41597-024-03380-3)

## How to get the database?
git clone git@github.com:NavandarM/PrimBrainLnc.git <br> 
or<br>
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
