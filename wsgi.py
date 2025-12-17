# wsgi.py

from Display_module_1_old import server  # <-- your Flask server exported in Tracker_mongo.py

# Some platforms look specifically for "application"
application = server
