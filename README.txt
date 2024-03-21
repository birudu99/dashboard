This is a sample project Ecomm-Evadella-Dashboard.

Create Virtual Environment for the project by using "python -m venv venv".

After cloning the project, install the dependencies.

For that we have to install just the requirments.txt file in which all the libraries are mentioned, 
by using command "pip install -r requirements.txt".

There is a file generatekeys.py first run that file to create and secure the credentials like username and password.

Make sure that the project is connected to the right local database in the evadella_mysql.py file, otherwise chage the
host, user, password and database attributes as necessary.

Run the main file to run the project by using "streamlit run EvaDella_App.py". Then it will run in the port localhost:8501.
