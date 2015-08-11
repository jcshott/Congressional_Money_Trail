## Lets make a web app! ##
from jinja2 import StrictUndefined

from flask import Flask, render_template, request, redirect, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from helper_functions import ordered_tuples

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
	#when a state is selected, show the list of legislators from that state
	state_selected = request.form.get('state_value')
	#get list of objects of senators & house members
	senators_state = Legislator.query.filter(Legislator.state == state_selected, Legislator.chamber == "Senate").all()

	senator1 = senators_state[0].serialize()
	senator2 = senators_state[1].serialize()

	house_state = Legislator.query.filter(Legislator.state == state_selected, Legislator.chamber == "House").all()
	
	members = []
	for item in house_state:
		member = item.serialize()
		members.append(member)

	return jsonify(state_selected=state_selected, senator1=senator1, senator2=senator2, members=members)

@app.route('/trail_map', methods=["GET"])
def show_trail_map():
	"""render the D3 map of contributions to selected Member of Congress"""
	member_choice = request.args.get("member")
	print "member choice: ", member_choice
	#need to query database for legislator information on the selected member and show in sidebar in trail_map.
	#need to query db for contributor info so I can create cool visuals.

	return render_template("trail_map.html")

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