# soletaal_app
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install flask
touch app.py requirements.txt
mkdir -p studio/{db,utils,templates,student,attendance,payment,expense}
mkdir -p studio/{student,attendance,payment,expense}/routes
mkdir -p studio/{student,attendance,payment,expense}/templates
touch studio/{student,attendance,payment,expense}/__init__.py
for i in {student,attendance,payment,expense}                
do
touch studio/${i}/${i}_routes.py
done
```
