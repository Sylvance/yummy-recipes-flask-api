""" Manage.py file"""
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import APP, DB
import os
import unittest
import coverage

# Initializing the manager
MANAGER = Manager(APP)

# Initialize Flask Migrate
MIGRATE = Migrate(APP, DB)

# Add the flask migrate
MANAGER.add_command('DB', MigrateCommand)

# Test coverage configuration
COV = coverage.coverage(
    branch=True,
    include='app/*',
    omit=[
        'app/controllers/__init__.py'
    ]
)
COV.start()

# Add test command
@MANAGER.command
def test():
    """
    Run tests without coverage
    :return:
    """
    tests = unittest.TestLoader().discover('tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

if __name__ == '__main__':
    MANAGER.run()
