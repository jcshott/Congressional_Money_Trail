# command line args (what to be updated & file(s) to use): legislators; contributions
import requests, os, csv, argparse

from model import  connect_to_db, db, Legislator, Contrib_leg, Contributors, Type_contrib, Contrib_pac, Industry
from server import app
from helper_functions import get_first_term_year

import psycopg2

def update_legislators():
	""" input = file handle from which to look for updates to legislators
		output = nothing

		checks for new legislators. they can be 1) filling empty seat or 2) replacing an occupied seat

	"""
	currently_loaded = db.session.query(Legislator.leg_id).all() #list of tuples => [(leg_id (known as crp_id in sunlight data,), (leg_id,)]
	loaded_ids = {tup[0]: True for tup in currently_loaded}

	# use this to keep track of currently serving members, we can then check against ones in db.
	# if its in our db but not in this list, then we need to delete from our db
	current_mem_ids = {}

	apikey = os.environ['SUNLIGHT_API_KEY']
	query_params = { 'apikey': apikey,
					'per_page': 'all', 
			       }

	endpoint = 'https://congress.api.sunlightfoundation.com/legislators/'
	# gets all current members of congress. need to find ones we don't already have in our system
	response = (requests.get(endpoint, params=query_params)).json()
	for entry in response['results']:
		crp_id = entry['crp_id']
		bioguide_id = entry['bioguide_id']
		first = entry['first_name']
		last = entry['last_name']
		nickname = entry['nickname']
		suffix = entry['name_suffix']
		title = entry['title']
		state = entry['state']
		party = entry['party']
		chamber = entry['chamber'].capitalize()
		twitter_id = entry.get('twitter_id', None)
		facebook_id = entry.get('facebook_id', None)
		if chamber =="Senate":
			sen_rank =  entry['state_rank'].capitalize()
			district = None
		else:
			district = int(entry['district'])  #only for house members
			sen_rank = None
		off_website = entry['website']
		open_cong_url = None
		pict_link = "https://theunitedstates.io/images/congress/225x275/"+bioguide_id+".jpg"
		first_elected = get_first_term_year(crp_id, apikey) #API call to SLF to get the year
		current_mem_ids[crp_id] = True
		# if the member is not already loaded, load it
		if crp_id not in loaded_ids:
			temp_legislator_object = Legislator(leg_id=crp_id, bioguide_id=bioguide_id, first=first, last=last, nickname=nickname, suffix=suffix, title=title, state=state, party=party, chamber=chamber, twitter_id=twitter_id, facebook_id=facebook_id, district=district, sen_rank=sen_rank, off_website=off_website, open_cong_url=open_cong_url, pict_link=pict_link, first_elected=first_elected)

			db.session.add(temp_legislator_object)

	# if member is in our db but isn't current member, remove from db 
	for x in loaded_ids.keys():
		if x not in current_mem_ids:
			member = Legislator.query.filter_by(leg_id = x).first()
			# get all contributions to that member and delete from table
			contributions = Contrib_leg.query.filter_by(leg_id= x).all()
			for item in contributions:
				db.session.delete(item)
			db.session.delete(member)

	db.session.commit()

def update_contributions(file_lst):
	""" input = list file handle from which to look for updates to contributions
		output = nothing

		inputs new contributions for current members of congress
		updates legislators table to recalculate new contributions JSON objects
	"""
	pass

def update_indiv_to_leg():
	""" will update individual to member contributions table & individual giver table (as necessary) """
	pass

def update_pac_to_leg():
	""" updates PAC to legislator contributions """
	pass

def update_pac_contributors():
	""" updates PAC contributor info table (as necessary)"""
	# will need to check if contributor id exists, if not, add otherwise, pass
	pass

def update_top_contributors():
	# this is where we'll update top contributors
	pass

def main():
	parser = argparse.ArgumentParser(description="update congressional money trail db")
	parser.add_argument("operation", help='define what you want to update. options are "legislators" or "contributions"')
	# will need to add for updating contributions tables
	args = parser.parse_args()
	if args.operation.lower() == "legislators":
		update_legislators()
	elif args.operation.lower() == "contributions":
		# this will need 3 additional arguments - the file names from CRP
		pass
	else:
		print "please use 'legislators' or 'contributions' as arguments"

if __name__ == "__main__":
    
    connect_to_db(app)
    main()
