# FSND Linux Server Project
A description for setting up a AWS Lightsail Linux instance and preparing it for deploying the FSND catalog app
# Connection Requirements

Public URL: [http://35.174.74.235.xip.io](http://35.174.74.235.xip.io)

IP Address: 35.174.74.235

SSH Port: 2200

Connection String:

ssh -i "/path/to/key/" grader@35.174.74.235 -p 2200

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

### Step 2: Create a New User (<new_user>)

One requirement is to create a new sudo user, '<new_user>' to replace the default login, 
and to disable root access.  You will be asked to create a password during this process and 
since the user will have sudo access, a password needs to be established.  The remaining 
questions can be completed as applicable.
Create the user id while logged in as the default sudo user Ubuntu:

`sudo adduser <new_user>`

It will prompt for a password. Add any password to that field. After the user gets created, run this command to give the grader sudo priviledges:

*The grader userid is granted sudo access through the following steps:*

`sudo visudo`

Once your in the visudo file, go to the section user privilege specification

root    ALL=(ALL:ALL) ALL

Add the following line to provide sudo access to your <new_user>

<new_user> ALL=(ALL:ALL) ALL

Eit the file

`sudo nano /etc/sudoers.d/<new_user>`

Add the line:

```
<new_user> ALL=(ALL:ALL) ALL
```

The <new_user> user is required to have a seperate keypair for ssh access. First you must make
the directory to hold the key pair:

`sudo mkdir /home/<new_user>/.ssh`

Next, create the file "authorized_keys" that will contain the key pair.

`touch /home/<new_user>/.ssh/authorized_keys`

Next the key that has been generate locally, via the ssh-keygen method or other, will need 
to be copied (preferred) or typed into the file we just created:

`sudo nano /home/<new_user>/.ssh/authorized_keys`

Another requirement of the project is to configure the SSH port for a non-standard port 2200.
Before beginning, access the networking tab in the Amazon Lightsail interface and allow this 
port through the firewall.  Failure to do this will knock you out of your server during the next
few steps.

### Step 3: Disable root

Disable both root login and password

`sudo nano /etc/ssh/sshd_config`

Update the ssh port

```
# What ports, IPs and protocols we listen for
# Port 22
Port 2200
```

Disable the root login by verify or changing the following parameter to "no"

```
# Authentication:
LoginGraceTime 120
#PermitRootLogin prohibit-password
PermitRootLogin no
StrictModes yes
```
Change to no to disable tunnelled clear text passwords

`PasswordAuthentication No`

Finally, restart the SSH service to assure changes are made effective.

`sudo service ssh restart`

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

Make sure remote access is not allowed.  By default, only local access
was allowed and can be determined by looking at the following files and
make sure no external IP addresses are listed:

`sudo nano /etc/postgresql/9.5/main/pg_hba.conf`

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

### Part 17: Installing PHP if Needed

If you're using the latest version of Ubuntu (16.04 or later), consider using PHP7.0 instead of PHP5. To do so, check if you already have PHP installed.

`php --version`

If you do not have PHP already installed, you will likely see a message such as

```
$ php --version
The program 'php' can be found in the following packages:
 * php7.0-cli
 * hhvm
Try: sudo apt install <selected package>
```

To install PHP from the Ubuntu repositories,


`sudo apt install php`
If you already have PHP installed, you will likely see something like

```
$ php --version
PHP 7.0.4-7ubuntu2 (cli) ( NTS )
Copyright (c) 1997-2016 The PHP Group
Zend Engine v3.0.0, Copyright (c) 1998-2016 Zend Technologies
    with Zend OPcache v7.0.6-dev, Copyright (c) 1999-2016, by Zend Technologies
```

At this point, Apache and PHP are installed and ready to go. A recent update to the Lucid distribution, however, requires a slight change to /etc/apache2/mods-available/php5.conf to re-enable interpretation in users' home directories -- previous distributions do not require this change. Simply open up this file in your favorite editor as root (a simple sudo gedit /etc/apache2/mods-available/php5.conf will suffice) and comment out (or remove) the following lines:

```
    <IfModule mod_userdir.c>
        <Directory /home/*/public_html>
            php_admin_value engine Off
        </Directory>
    </IfModule>
```
If you don't see anything starting with PHP in /etc/apache2/mods-available, you likely need to install libapache2-mod-php. Run

`sudo apt install libapache2-mod-php`

After running it, you should see phpx.conf and phpx.load where x is the current PHP version. For example, at the time of this writing, I see php7.0.conf and php7.0.load. Edit the conf file as shown above.

Once this has been done, restart apache2 with the usual sudo /etc/init.d/apache2 restart and PHP should be successfully installed and working.

Make sure you have userdir enabled. If it is not enabled, run the following to enable it

`sudo a2enmod userdir`

Security note: Running PHP scripts in users' home directories was not disabled for a frivolous reason -- PHP is a full programming language, and as such, can be used by attackers in nefarious ways. Ideally, the PHP engine should only be enabled for users you (the system administrator) trust, and even then sparingly. To do this, instead of removing the above lines, create a file (as root) called /etc/apache2/conf.d/php-in-homedirs.conf with the following contents:

```
<IfModule mod_userdir.c>
    <Directory /home/$USERNAME/public_html>
        php_admin_value engine On
    </Directory>
</IfModule>
```

Simply replace the $USERNAME with the user name of the user you wish to allow PHP access to. Also note that the <Directory> section may be repeated as many times as is necessary. Save the file, and restart Apache with a sudo /etc/init.d/apache2 restart and PHP should only be enabled for the users listed in this file. See the Apache documentation on the Directory tag for more information.

### Giving Credit Where Credit is Due
* Countless hours on Udacity Forums scowering information from bits and peices of answers
* Udacity FSND Lectures: [https://www.digitalocean.com/community/tutorials/how-to-setup-a-firewall-with-ufw-on-an-ubuntu-and-debian-cloud-server](https://www.digitalocean.com/community/tutorials/how-to-setup-a-firewall-with-ufw-on-an-ubuntu-and-debian-cloud-server)
* Ask Ubuntu [https://askubuntu.com/questions/194/how-can-i-install-just-security-updates-from-the-command-line](https://askubuntu.com/questions/194/how-can-i-install-just-security-updates-from-the-command-line)
* harushimo's GitHub Readme: [https://github.com/harushimo/linux-server-configuration](https://github.com/harushimo/linux-server-configuration)
* DigitalOcean: [https://www.digitalocean.com/community/tutorials/how-to-secure-postgresql-against-automated-attacks](https://www.digitalocean.com/community/tutorials/how-to-secure-postgresql-against-automated-attacks)
* Ubuntu (of course) [https://www.ubuntu.com/](https://www.ubuntu.com/)
* Apache/mod-wsgi: [http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/](http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/)
* Postgresql: [https://www.postgresql.org/docs/current/static/index.html](https://www.postgresql.org/docs/current/static/index.html)
* Abigail Mathews's GitHub Readme: [https://github.com/AbigailMathews/FSND-P5](https://github.com/AbigailMathews/FSND-P5)
