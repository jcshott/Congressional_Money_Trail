import requests, os, sqlite3, operator
from model import connect_to_db, db, Legislator, Contrib_leg, Contributors, Type_contrib, Contrib_pac


#need a connection to sqldb directly for quicker queries on db
db_connection = sqlite3.connect("contributions.db", check_same_thread=False)
db_cursor = db_connection.cursor()


def create_contribution_dict(member_choice_id):
	"""Create a dictionary from my database data that is selected based on user input

	takes in the id of a Member of Congress (that is sent to the server via a GET request)
	returns a dictionary that can be jsonified

	"""

	#put all this into a dictionary so we can jsonify for D3 to interpret.
	contributions = {}

	#sub/children dictionaries for varies branches of tree
	sum_i_contributions = {}
	sum_p_contributions = {}

###################################################################
## Queries and data analysis that goes into the branches #####
###################################################################

	#sum of contributions from individuals to selected legislator
	QUERY = """
        SELECT sum(amount)
        FROM contrib_legislators JOIN contributors USING (contrib_id)
        WHERE contrib_legislators.leg_id = ? AND contributors.contrib_type = 'I'
        """
	db_cursor.execute(QUERY, (member_choice_id,))

	indiv_contributions = db_cursor.fetchall()
	indiv_contributions = float(indiv_contributions[0][0])

	QUERY = """
        SELECT sum(amount)
        FROM contrib_legislators JOIN contributors USING (contrib_id)
        WHERE contrib_legislators.leg_id = ? AND contributors.contrib_type = 'C'
        """
	db_cursor.execute(QUERY, (member_choice_id,))

	pac_contributions = db_cursor.fetchall()
	pac_contributions = float(pac_contributions[0][0])
	

	#take in selected member id, get member object from db and extract information to be displayed on node in browser.
	member_obj = Legislator.query.get(member_choice_id)
	if member_obj.chamber == "Senate":
		if member_obj.nickname:
			member = "%s. %s %s (%s - %s) %s" % (member_obj.title, member_obj.nickname, member_obj.last, member_obj.party, member_obj.state, member_obj.sen_rank)
		else:
			member = "%s. %s %s (%s - %s) %s" % (member_obj.title, member_obj.first, member_obj.last, member_obj.party, member_obj.state, member_obj.sen_rank)

	if member_obj.chamber == "House":
		if member_obj.nickname:
			member = "%s. %s %s (%s - %s %d)" % (member_obj.title, member_obj.nickname, member_obj.last, member_obj.party, member_obj.state, member_obj.district)
		else:
			member = "%s. %s %s (%s - %s %d)" % (member_obj.title, member_obj.first, member_obj.last, member_obj.party, member_obj.state, member_obj.district)

	sum_i_contributions["name"] = "Contributions from Individuals: " '${:,.0f}'.format(indiv_contributions)
	sum_p_contributions["name"] = "Contributions from PACs: " '${:,.0f}'.format(pac_contributions)

	# sum_i_contributions["size"] = (indiv_contributions/(indiv_contributions + pac_contributions))*100
	# sum_p_contributions["size"] = (pac_contributions/(indiv_contributions + pac_contributions))*100

	contributions["name"] = member
	contributions["children"] = [sum_i_contributions, sum_p_contributions]

	return contributions


def get_first_term_year(leg_id, apikey):
	query_params = { 'apikey': apikey,
				     'fields': "terms.start",
				     'crp_id': leg_id
			       }

	endpoint = 'https://congress.api.sunlightfoundation.com/legislators/'
	response = (requests.get(endpoint, params=query_params)).json()

	if response['results'] == []:
		return 0	
		#if brand new member, set to zero so when calculate time in office, we get the current year
	
	else:	
		first_term_year = int(response['results'][0]['terms'][0]['start'][:4]) #get just the year of the first term in office from the gnarly dict returned
		return first_term_year

def ordered_tuples(dictionary):
        orig_tuples = dictionary.iteritems()
        ordered_tuples = sorted(orig_tuples, key=lambda dictionary: dictionary[1])
        
        return ordered_tuples