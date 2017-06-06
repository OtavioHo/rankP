# catalog-app
Catalog app

## Description
This project works with a database (PostgreSQL) and with the flask framework for python to create an catalog app.
The project contain a own authorization system and a third-party one (Google+).

## Whats included
 - /static
 - /templates
 - databasesetup.py
 - project.py
 - Vagrantfile
 - pg_config.sh
 
### /static
Repository where the static file such as css, javascript and images are.

### /templates
Repository to keep all the html files

### databasesetup.py
Python file that setup the catalog database

### project.py
Main file that contains all the backend code for the app

### Vagrantfile and pg_config.sh
Files to config the Virtual Machine and setup the environment

## How to setup the environment
First you have to install VirtualBox and Vagrant.
When both are installed, clone this repository, navigate to the folder and run "vagrant up" on your terminal.
With the vagrant configurated run "vagrant ssh".
then navigate to /vagrant

## How to run the App
In the /vagrant folder run the project.py file.
Go to your browser and access http://localhost:3000

### JSON endpoints
To access the JSON endpoints:
 - all categories: http://localhost:3000/catalog/categories/JSON
 - items form a specific categorie: http://localhost:3000/catalog/[categorie_id]/JSON
 - all items: http://localhost:3000/catalog/items/JSON
 - specific item: http://localhost:3000/catalog/items/[item_id]/JSON
