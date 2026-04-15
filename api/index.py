import os
import sys

os.chdir(os.path.dirname(os.path.dirname(__file__)))

from main import app

handler = app
