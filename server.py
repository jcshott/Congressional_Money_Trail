## Lets make a web app! ##
from jinja2 import StrictUndefined

from flask import Flask, render_template, request, redirect, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, Legislator, Contrib_leg, Contributors, Type_contrib, Contrib_pac


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():
	"""Homepage"""

	return render_template("homepage.html")

@app.route('/login')
def log_in():
	"""add to session if they log-in via FB or Twitter allows to share via social media"""

@app.route('/welcome')
def welcome():
	"""page where user selects Member of Congress to map"""
	#code here!
	#states = [Alabama, Montana, California, District of Columbia]
	return render_template("welcome.html", states=states)

@app.route('/trail_map')
def show_trail_map():
	"""render the D3 map of contributions to selected Member of Congress"""

	#code here!	

##may not need - will know after understand D3 better
@app.route('/PAC_visual')
def show_pac_info():
	"""Show the contributors to selected PAC"""


@app.route('/image_share')
def share_image():
	"""send captured image to social media sites"""
	#code - should send captured image to a new page with options listed to share



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()