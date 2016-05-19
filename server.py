from jinja2 import StrictUndefined
from flask import Flask, render_template, request, redirect, flash, session, jsonify, g
from flask_debugtoolbar import DebugToolbarExtension
from helper_functions import ordered_tuples
from model import connect_to_db, db, Legislator, Contrib_leg, Contributors, Type_contrib, Contrib_pac
import operator, os
from sunlight import congress
import googlemaps
import psycopg2
import urlparse


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "ABCDEF")
app.secret_key = SECRET_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

PORT = int(os.environ.get("PORT", 5000))
#set debug-mode to false for deployed version but true locally
DEBUG = "NO_DEBUG" not in os.environ

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined

STATE_DICT = {
        'AK': 'Alaska', 'AL': 'Alabama', 'AR': 'Arkansas', 'AS': 'American Samoa', 'AZ': 'Arizona', 'CA': 'California', 'CO': 'Colorado',
        'CT': 'Connecticut', 'DC': 'District of Columbia', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'GU': 'Guam', 'HI': 'Hawaii',
        'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'MA': 'Massachusetts',
        'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan', 'MN': 'Minnesota', 'MO': 'Missouri', 'MP': 'Northern Mariana Islands', 'MS': 'Mississippi',
        'MT': 'Montana', 'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico',
        'NV': 'Nevada', 'NY': 'New York', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'PR': 'Puerto Rico', 'RI': 'Rhode Island',
        'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VA': 'Virginia', 'VI': 'Virgin Islands',
        'VT': 'Vermont', 'WA': 'Washington', 'WI': 'Wisconsin', 'WV': 'West Virginia', 'WY': 'Wyoming'}


# @app.route('/')
# def index():
# 	"""Homepage  """
#
# 	return render_template("homepage.html")


@app.route('/')
def show_main_page():
	"""all the magic"""

	if session:
		session.clear()

	states = ordered_tuples(STATE_DICT)

	# also need info in dict form to access on profile div
	state_dict = STATE_DICT

	return render_template("main.html", states=states, state_dict=state_dict)


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

	gmapKey = os.environ.get('Google_Maps_API_Key')
	gmaps = googlemaps.Client(key=gmapKey)

	address = request.form.get("address")
	# Geocoding and address
	geocode_result = gmaps.geocode(address)

	#parse the geocode result to get lat/long
	geocode_info = geocode_result[0]
	geometry = geocode_info.get('geometry')
	location_data = geometry.get("location")
	latitude = location_data.get('lat')
	longitude = location_data.get('lng')

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

@app.route('/trail_map', methods=["POST"])
def show_trail_map():
	"""Page where info on selected Member of Congress will display"""

	member_choice_id = request.form.get("member")
	session["member_choice_id"] = member_choice_id

	member = Legislator.query.filter_by(leg_id = member_choice_id).first()

	member_info = member.serialize()

	states = STATE_DICT

	return render_template("memberprofilehold.html", member_info=member_info, states=states)


@app.route('/map_info.json', methods=["GET"])
def get_tree_data():
	""" creating the json object that D3 needs to render the tree map.  the main function is defined in
	helper_functions file """

	member_choice_id = session.get("member_choice_id")

	selected_member = Legislator.query.filter_by(leg_id = member_choice_id).first()

	try:
		contributions = selected_member.top_contributors
		return jsonify(contributions)

	except Exception, e:
		print "error"
		return "None"


if __name__ == "__main__":
    connect_to_db(app)

    # Use the DebugToolbar set debug to True if using
    # DebugToolbarExtension(app)
    app.run(debug=DEBUG, host="0.0.0.0", port=PORT)
