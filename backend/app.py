import os
from flask import Flask

# Configure Flask to use the project-level 'static' and 'templates' directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_FOLDER = os.path.join(BASE_DIR, 'app')
TEMPLATES_FOLDER = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, static_folder=STATIC_FOLDER, template_folder=TEMPLATES_FOLDER)

# Import the original routes and settings from the relocated app module
from scripts.app import *  # type: ignore  # noqa: E402,F401,F403
