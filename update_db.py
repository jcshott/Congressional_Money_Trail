# command line args (what to be updated & file(s) to use): legislators; contributions
import requests, os, argparse

from model import  connect_to_db, db, Legislator, Contrib_leg, Contributors, Type_contrib, Contrib_pac, Industry
from server import app
from helper_functions import get_first_term_year
from string import capwords
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

def update_indiv_to_leg(file_path):
	""" will update individual to member contributions table & individual giver table (as necessary) """

	cont_id_dict = {}

	file_open = open(file_path)
	
	for index, line in enumerate(file_open):
		value = line.split("|,|")
		# TODO: change this to checking if val[4] (crp_id) is in our legislator table (leg_id) 
		if Legislator.query.get(value[4]):
                # per CRP documentation. to make sure only get indiv. donors, check that contrib_id has a value. first need to strip whitespace.
                # this worked on the test set but not when running the full thing, non-I-contributors still got in. unsure why. so, just deleted 
                # from db directly by deleting all from contrib_legislators table where id was empty string.
			value[2].replace(" ", "")
			if value[2] != "":
				contrib_id = value[2].strip()
				FEC_trans_id = value[1]
				name = capwords(value[3])
				contrib_type = "I"
				contrib_state = value[9]
				cycle = value[0].strip('|')
				leg_id = value[4]

				#first split of line makes it so there is one grouping of industry, data & amount given so need to further parse that.
				split_ind_amt_data = value[7].split(',')
				if split_ind_amt_data[0]:
					if split_ind_amt_data[0] == "NONE":
						industry_id = None
					else:
						industry_id = split_ind_amt_data[0].strip('|')
						
						if not Industry.query.get(industry_id):
							industry_id = "unknown"
				else:
					industry_id = None

				amount = int(float(split_ind_amt_data[2]))

				# need to weed out multiples of the contributor going into table - otherwise fails PK constraint on contributor_id.
				# add the id as a key and set initial value to 1 but increment value every time you have someone with that id.
				cont_id_dict[contrib_id] = cont_id_dict.get(contrib_id, 0) + 1


				if industry_id[0:2] != "Z9":
				#allow for the person to be added to Contributor table first time encountered but not after.
				# also check for contributor in our table already. .first() returns the item or None so only add if we get None
				# we don't want to add to the Contributors but we do want to add the amount to Contrib_leg table

					if cont_id_dict.get(contrib_id) == 1 and not Contributors.query.filter_by(contrib_id=contrib_id).first():
						temp_contrib_obj = Contributors(contrib_id=contrib_id, name=name, contrib_type=contrib_type, industry_id=industry_id, contrib_state=contrib_state)
						db.session.add(temp_contrib_obj)

					temp_contrib_leg_obj = Contrib_leg(contrib_id=contrib_id, FEC_trans_id=FEC_trans_id, leg_id=leg_id, amount=amount, cycle=cycle)
					db.session.add(temp_contrib_leg_obj)

				if index % 100 == 0:
					db.session.commit()

	db.session.commit()
	print "individuals data successfully added ", file_path
	file_open.close()

def update_pac_to_leg(file_path):
	""" updates/adds to PAC to legislator contributions """

	file_open = open(file_path)

	for index, line in enumerate(file_open):
		value = line.split(",")
		leg_id = value[3].strip('|')

		if Legislator.query.get(leg_id):
			cont_type = value[7].strip('|')
			industry_id = value[6].strip('|')

        #z9 and z4 are considered non-contribution types -> transfers
		if industry_id[0:2] != "z9" and industry_id[0:2] != "z4":
			if cont_type != "24A" and value[7] != "24N":
				cycle = value[0].strip('|')
				FEC_trans_id = value[1].strip('|')
				contrib_id = value[2].strip('|')
				amount = int(float(value[4]))

				temp_contrib_leg_obj = Contrib_leg(contrib_id=contrib_id, FEC_trans_id=FEC_trans_id, leg_id=leg_id, amount=amount, cycle=cycle)
				db.session.add(temp_contrib_leg_obj)  

				if index % 100 == 0:
					db.session.commit()

	db.session.commit()
	print "pac contribution data successfully added ", file_path
	file_open.close()

def update_pac_contributors(file_path):
	""" updates PAC contributor info table (as necessary)"""
	# will need to check if contributor id exists, if not, add otherwise, pass
	cont_id_dict = {}

	file_open = open(file_path)

	for index, line in enumerate(file_open):
		value = line.split(",")
		contrib_id = value[1].strip('|')      
		contrib_type = "C"

		#check if contributor has been entered by checking db and dict of those already in db
		if contrib_id not in cont_id_dict and not Contributors.query.get(contrib_id):
			cont_id_dict.setdefault(contrib_id, True)
			name = value[2].strip('|')

			if value[9]:
				industry_id = value[9].strip("|")

				if not Industry.query.get(industry_id):
					industry_id = "unknown"
			else:
				industry_id = "unknown"
			temp_contrib_obj = Contributors(contrib_id=contrib_id, industry_id=industry_id, name=name, contrib_type=contrib_type)
			db.session.add(temp_contrib_obj)

	db.session.commit()
	print "pac contributor info data successfully added", file_path
	file_open.close()


def update_top_contributors():
	# this is where we'll update top contributors
	currently_loaded = db.session.query(Legislator.leg_id).all() #list of tuples => [(leg_id (known as crp_id in sunlight data,), (leg_id,)]
	loaded_ids = {tup[0]: True for tup in currently_loaded}
	for item in loaded_ids:
	#get the member object from the database
		try:
			member = Legislator.query.filter_by(leg_id = item).first()

			#get the dictionary to be stored as json using method
			contribution_dict = member.create_contribution_dict()

			# add to the legislator table
			member.top_contributors = contribution_dict
			db.session.commit()
		except Exception, e:
			print "Exception: ", e
			print "not loaded: ", item
			continue

def main():
	parser = argparse.ArgumentParser(description="update congressional money trail db")
	parser.add_argument("operation", help='define what you want to update. options are "legislators", "pac_contributions", "indiv_contributions", or "update_top_contributors"')
	args = parser.parse_args()
	if args.operation.lower() == "legislators":
		update_legislators()
	elif args.operation.lower() == "pac_contributions":
		# this will need additional arguments - the file names from CRP
		file_handle_contributions = raw_input("Please indicate source file for PAC contribution data: ")
		file_handle_PACs = raw_input("Please indicate source file for PAC informational data: ")
		update_pac_to_leg(file_handle_contributions)
		update_pac_contributors(file_handle_PACs)
	elif args.operation.lower() == "indiv_contributions":
		file_handle = raw_input("Please indicate source file for individual data: ")
		update_indiv_to_leg(file_handle)
	elif args.operation.lower() == "update_top_contributors":
		update_top_contributors()
	else:
		print "please use 'legislators', 'pac_contributions' or 'indiv_contributions', or 'update_top_contributors' as additional argument"

if __name__ == "__main__":
    
	connect_to_db(app)
	main()

