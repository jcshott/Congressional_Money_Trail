## Lets make a web app! ##
from jinja2 import StrictUndefined
from flask import Flask, render_template, request, redirect, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from helper_functions import ordered_tuples, create_contribution_dict
from model import connect_to_db, db, Legislator, Contrib_leg, Contributors, Type_contrib, Contrib_pac
import sqlite3
import operator

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
	senators_state = Legislator.query.filter(Legislator.state == state_selected, Legislator.chamber == "Senate").all()

	#can't send objects to the ajax to parse so need to serialize (fn defined on class Legislator) to send a json object
	senator1 = senators_state[0].serialize()
	senator2 = senators_state[1].serialize()

	house_state = Legislator.query.filter(Legislator.state == state_selected, Legislator.chamber == "House").all()
	
	#same except b/c I don't know how many members there are for any given state, need to created list of json objects.
	members = []
	for item in house_state:
		member = item.serialize()
		members.append(member)

	#sends a json object where each of the below variables is a key: value like in dict.  
	#passing members as a list
	return jsonify(state_selected=state_selected, senator1=senator1, senator2=senator2, members=members)

@app.route('/trail_map', methods=["GET"])
def show_trail_map():
	"""Page where D3 map and other info on selected Member of Congress will display"""
	
	member_choice_id = request.args.get("member")

	session["member_choice_id"] = member_choice_id

	return render_template("trail_map.html")


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