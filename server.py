## Lets make a web app! ##
from jinja2 import StrictUndefined
from flask import Flask, render_template, request, redirect, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from helper_functions import ordered_tuples, create_contribution_dict
from model import connect_to_db, db, Legislator, Contrib_leg, Contributors, Type_contrib, Contrib_pac
import sqlite3, operator, os
from sunlight import congress

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

#need a connection to sqldb directly for quicker queries on db
db_connection = sqlite3.connect("contributions.db", check_same_thread=False)
db_cursor = db_connection.cursor()

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():
	"""Homepage  """

	return render_template("homepage.html")


@app.route('/login')
def log_in():
	"""add to session if they log-in via FB or Twitter allows to share via social media"""

@app.route('/welcome')
def welcome():
	"""page where user selects legislator to map"""
	#passing info to jinja template so I can make drop-down of all states/territories in US
	state_dict = {
        'AK': 'Alaska', 'AL': 'Alabama', 'AR': 'Arkansas', 'AS': 'American Samoa', 'AZ': 'Arizona', 'CA': 'California', 'CO': 'Colorado',
        'CT': 'Connecticut', 'DC': 'District of Columbia', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'GU': 'Guam', 'HI': 'Hawaii',
        'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'MA': 'Massachusetts',
        'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan', 'MN': 'Minnesota', 'MO': 'Missouri', 'MP': 'Northern Mariana Islands', 'MS': 'Mississippi',
        'MT': 'Montana', 'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico',
        'NV': 'Nevada', 'NY': 'New York', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'PR': 'Puerto Rico', 'RI': 'Rhode Island',
        'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VA': 'Virginia', 'VI': 'Virgin Islands',
        'VT': 'Vermont', 'WA': 'Washington', 'WI': 'Wisconsin', 'WV': 'West Virginia', 'WY': 'Wyoming'}
  
	states = ordered_tuples(state_dict)

	return render_template("welcome.html", states=states)

@app.route('/state_info', methods=["POST"])
def show_legislators():
	"""when a state is selected, show the list of legislators from that state"""

	#post request will send dict item so on html side, i send a dictionary with the state_value: value pair
	state_selected = request.form.get('state_value')

	#get list of objects of senators & house members
	state_legislators = Legislator.query.filter(Legislator.state == state_selected).all()

	senators = []
	representatives = []
	
	for member_object in state_legislators:
		if member_object.chamber == "Senate":
			senator = member_object.serialize()
			senators.append(senator)
		
		else:
			rep = member_object.serialize()
			representatives.append(rep)

	#account for D.C./territories with no senators.
	if not senators:
		return jsonify(state_selected=state_selected, representatives=representatives)
	
	else:
		return jsonify(state_selected=state_selected, senators=senators, representatives=representatives)

@app.route('/address_search', methods=["POST"])
def show_members_for_address():
	"""show legislators for user based on address search
		takes lat/long from google maps API and returns list of legislators

	"""

	latitude = request.form.get('latitude')
	longitude = request.form.get('longitude')
	
	#API call to Sunlight Foundation for legislators by lat/lon
	legislators_list = congress.locate_legislators_by_lat_lon(lat=latitude, lon=longitude)

	legislators_by_address = []
	crp_ids = []
	legislators_to_serialize = []

	for legislator in legislators_list:
		crp_id = legislator.get('crp_id')
		crp_ids.append(crp_id)
		
	for item in crp_ids:
		member = Legislator.query.filter_by(leg_id = item).first()
		legislators_to_serialize.append(member)

	for item in legislators_to_serialize:
		legislator = item.serialize()
		legislators_by_address.append(legislator)

	return jsonify(legislators_by_address=legislators_by_address)

@app.route('/trail_map', methods=["GET"])
def show_trail_map():
	"""Page where D3 map and other info on selected Member of Congress will display"""
	
	member_choice_id = request.args.get("member")

	session["member_choice_id"] = member_choice_id

	member = Legislator.query.filter_by(leg_id = member_choice_id).first()

	member_info = member.serialize()

	return render_template("trail_map.html", member_info=member_info)


@app.route('/map_info.json', methods=["GET"])
def get_tree_data():
	""" creating the json object that D3 needs to render the tree map.  the main function is defined in
	helper_functions file """

	member_choice_id = session.get("member_choice_id")
	
	contributions = create_contribution_dict(member_choice_id)

	return jsonify(contributions)
	

@app.route('/image_share')
def share_image():
	"""send captured image to social media sites"""
	#code - should send captured image to a new page with options listed to share

@app.route('/about')
def describe_page():
	""" Share info on where the data came from and some of the inconsistencies - include notes on how hard tracking contributions really is """

	return render_template("about_the_site.html")

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()