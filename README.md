# FSND Linux Server Project
A description for setting up a AWS Lightsail Linux instance and preparing it for deploying the FSND catalog app
# Linux Server Configuration

## Overview of the Project
As the final project of the Udacity FullStack Nanodegree program, this exercise will satify the requirements to start a new Linux Ubuntu instance on the Amazon Lightsail platform.  This documentation will walk through the process of establishing the required updates, security, and platform following the requirements rubric in the Udacity Nanodegree program.  To save on duplication, the step-by-step requirements in the Linux Server Configuration - "Get started on Lightsail" will not be duplicated here.

## Establishing the Server Post Creating the Instance in Lightsail
This section outlines the steps taken to secure the server instance and load the Udacity "Catalog" project to run on the server.

### Step 1: Log into the Server
*Access the system through the Lightsail web SSH interface*

*Update Packages*

Since this base image from Amazon will not have recieved the latest code changes to the Ubuntu platform, we need to get these before we start anything else:
First get an updates that are availible.

`sudo apt-get update ` 

Second get any upgrades that are availible.
`sudo apt-get upgrade`

Finally, this instance showed that there were four security upgrades that had not been updated so the following is required to handle those upgrades:
`sudo unattended-upgrades -d`

### Step 2: Create a New User (grader)

One requirement by Udacity is to create a new sudo user, 'grader' to replace the default login, 
and to disable root access.  You will be asked to create a password during this process and 
since the user will have sudo access, a password needs to be established.  The remaining 
questions can be completed as applicable.
Create the user id while logged in as the default sudo user Ubuntu:

`sudo adduser grader`

*The grader userid is granted sudo access through the following steps:*

First, copy the original ubuntu user's sudoer file:
'cp /etc/sudoers.d/ubuntu /etc/sudoers.d/grader`

Second edit the file
`sudo nano /etc/sudoers.d/grader`

Edit the line:

```
ubuntu ALL=(ALL:ALL) ALL to
grader ALL=(ALL:ALL) ALL
```

The grader user is required to have a seperate keypair for ssh access. First you must make
the directory to hold the key pair:

`sudo mkdir /home/grader/.ssh`

Next, create the file "authorized_keys" that will contain the key pair.

'touch /home/grader/.ssh/authorized_keys`

Next the key that has been generate locally, via the ssh-keygen method or other, will need 
to be copied (preferred) or typed into the file we just created:

`sudo nano /home/grader/.ssh/authorized_keys`

Another requirement of the project is to configure the SSH port for a non-standard port 2200.
Before beginning, access the networking tab in the Amazon Lightsail interface and allow this 
port through the firewall.  Failure to do this will knock you out of your server during the next
few steps.

### Step 3: Disable root

Disable both root login and password
```
sudo nano /etc/ssh/sshd_config
sudo service ssh restart
```
### Step 4: Configure the ufw Firewall

Note: as we configured SSH on port 2200, we will not open port 22.  This must be done before
starting the firewall or we will completely loose access to the server!
We will also open ports 80 for the standard web server port and port 123 for the Network Time
Protocal (or NTP).

```
sudo ufw default deny incoming
sudo ufw default allow outgoing

sudo ufw allow 2200
sudo ufw allow 2200/tcp

sudo ufw allow 80
sudo ufw allow 80/tcp

sudo ufw allow 123
sudo ufw allow 123/tcp
```
Activate the firewall:

`sudo ufw enable`
Verify that your firewall is running:

`sudo ufw status`

### Step 5: Configure the Time Zone to UTC

Access the time-zone setting by entering:

`sudo dpkg-reconfigure tzdata`

This is a menu driven tool. On the second page bottom you
will find UTC.  Per the Udacity rubric, select UTC and exit
the program.


### Part 6: Install Apache and mod-wsgi for a Python Flask Application

First, install Apache:

`sudo apt-get install apache2`

Access your server's IP address and you should now see the Apache welcome page.

Next, install WSGI:
```
sudo apt-get install libapache2-mod-wsgi python-dev
sudo a2enmod wsgi
```

Restart Apache so that latest changes are applied.

`sudo service apache2 restart`


### Part 7: Install git

Install git with the following command:

`sudo apt-get install git`

Install the catalog application created earlier in the Udacity FSND program:
```
sudo git clone https://github.com/ssicet/FSND-Linux-Server-Project catalog
```

Next, change your current directory to the /var/www/catalog directory just created.

`cd /var/www/catalog'

Next, you will need to edit the __init__.py file

'sudo nano __init__.py`

Edit the last two lines of the program so that Apache can handle the IP and Port Assignment.
The last two lines of the project should look like this:
```
if __name__ == '__main__':
    app.run()
```

*Alternative*

In place of git, if you have not stored your repository in GitHub you can use a file transfer
program such as FileZilla to transfer you application to your server.

The connection parameters for the FTP will be the same as the user (grader) and requires the use
of the key established previously.

### Part 7: Install Python Libraries used in your program

*Install PIP*

`sudo apt-get install python-pip`


*Install Flask*

`sudo pip install Flask`

*Install SQLAlchemy*

`sudo pip install Flask-SQLAlchemy`

*Install SeaSurf*

`sudo pip install Flask-SeaSurf`

*Install Oauth2*

`sudo pip install oauth2client`

*Install Support for Postgres*

```
sudo apt-get install libpq-dev
sudo pip install psycopg2
```

### Part 8: Configure git Folder Restriction

Create a .htaccess file to restrict access to any .git files 

`sudo nano /var/www/catalog/.htaccess`

Create the entry: 

`RedirectMatch 404 /\.git`

Save the file.


### Part 9: Configure Apache Application

Create a new confi file for the catalog application:

`sudo nano /etc/apache2/sites-available/catalog.conf`

Copy/Paste the following into the file:

```
<VirtualHost *:80>
     ServerName  54.175.207.172
     ServerAdmin ridgewaymerrillb@gmail.com
     #Location of the items-catalog WSGI file
     WSGIScriptAlias / /var/www/catalog/catalog.wsgi
     #Allow Apache to serve the WSGI app from our catalog directory
     <Directory /var/www/Catalog/catalog/>
          Order allow,deny
          Allow from all
     </Directory>
     #Allow Apache to deploy static content
     Alias /static /var/www/catalog/catalog/static
     <Directory /var/www/catalog/catalog/static/>
        Order allow,deny
        Allow from all
     </Directory>
      ErrorLog ${APACHE_LOG_DIR}/error.log
      LogLevel warn
      CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

Disable the default Apache Page shown earlier and activate the config file / site
we just created.

```
sudo a2dissite 000-default
sudo a2ensite catalog
sudo service apache2 reload
```


### Part 10: Configure .wsgi file

Create the file by typing:

`sudo nano /var/www/catalog/catalog.wsgi`

Paste the following:

```
import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.append('/var/www/catalog')
sys.path.append('/var/www/catalog/catalog')

from catalog import app as application
application.secret_key='super_secret_key'
```

Save the file and exit nano

### Part 11: Install and Configure Postgresql

Install the Postgres SQL Application:

`sudo apt-get install postgresql`

Make sure remote access is not allowed:

`sudo nano /etc/postgresql/9.3/main/pg_hba.conf`

Create a password for postgres:

`sudo passwd postgres`

Create a password to work as the postgres user

### Part 12: Create Postgres User and Database for the Application

First, switch user to postgres and enter the application:

```
sudo su postgres
psql
```

Next, create the user (will need to match your application user and password), the database,
and the permissions to the database:

```
>> CREATE USER catalog;
>> ALTER USER catalog WITH PASSWORD 'catalog';
>> CREATE DATABASE catalog WITH OWNER catalog;
>> \c catalog
>> REVOKE ALL ON SCHEMA public FROM public;
>> GRANT ALL ON SCHEMA public TO catalog;
>> \q
```

Exit Postgres and return to user 'grader':

'su grader'

Restart Postgres Server to assure changes have taken affect:

`sudo service postgresql restart`

### Part 13: Start Database and Load the Seed Data

In /var/www/catalog create the tables by running in Python:

`python database_setup.py` 

Load seed data

`python database_load.py` 

### Part 14: Google Issues and OAuth

This is what should have been the easiest part but was difficult for no reason at all.  While 
the full URL for the site is ec2-35-174-74-235.compute-1.amazonaws.com there is apparently a 
bug with Google's oauth2 and this site is not allowed.  20+ hours of time was spent trying to 
figure this out as everything else will work except signing in to Google.  There is nothing
on the internet that I could find that addresses this, so the following is required:

Access the Google Credentials page and enter the following as authorized Javascript URL: 

http://35.174.74.235.xip.io

Make sure to hit the save button.

Download a fresh copy of your client_secrets.json file and upload to the server.  I used 
Filezilla to accomplish but git can be used as well.  The locations of this file were changed 
in advance of uploading to reflect the correct location on the file in the directory structure.

### Part 15: Launch Site

Restart the server one additional time to make sure all configurations have been applied:

`sudo service apache2 reload`

If for any reason Apache fails to restart, as mine did many times due to errors on my part,
be sure to use the log file to check your errors.  Do so by entering:

`sudo nano /var/log/apache2/error.log`

### Part 16: Access the Site

Log into the site from any web browser at the following URL:

[http://35.174.74.235.xip.io](http://35.174.74.235.xip.io)

Accessing by the IP only or the [ec2-35-174-74-235.compute-1.amazonaws.com](ec2-35-174-74-235.compute-1.amazonaws.com) will allow you to 
see the site but will *NOT ALLOW YOU TO LOG INTO GOOGLE*

### Giving Credit Where Credit is Due
* Countless hours on Udacity Forums scowering information from bits and peices of answers
* harushimo's GitHub Readme: [https://github.com/harushimo/linux-server-configuration](https://github.com/harushimo/linux-server-configuration)
* Udacity FSND Lectures: [https://www.digitalocean.com/community/tutorials/how-to-setup-a-firewall-with-ufw-on-an-ubuntu-and-debian-cloud-server](https://www.digitalocean.com/community/tutorials/how-to-setup-a-firewall-with-ufw-on-an-ubuntu-and-debian-cloud-server)
* Apache/mod-wsgi: [http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/](http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/)
* Postgresql: [http://killtheyak.com/use-postgresql-with-django-flask/](http://killtheyak.com/use-postgresql-with-django-flask/)
* Abigail Mathews's GitHub Readme: [https://github.com/AbigailMathews/FSND-P5](https://github.com/AbigailMathews/FSND-P5)
