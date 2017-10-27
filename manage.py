""" Manage.py file"""
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import APP, DB
import os

# Initializing the manager
MANAGER = Manager(APP)

# Initialize Flask Migrate
MIGRATE = Migrate(APP, DB)

# Add the flask migrate
MANAGER.add_command('DB', MigrateCommand)

if __name__ == '__main__':
    MANAGER.run()
