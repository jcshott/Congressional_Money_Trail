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

###################################################################
## Queries and data analysis that goes into the branches #####
###################################################################

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

	## use dictionaries to store how much each indiv person/pac gives to the member then can sort and get top contributors
	indiv_to_mem_dict = {}
	pac_to_mem_dict = {}

	### Get ID and amount donated to Member of Congress for Indiv. & PACs. will use to calculate other info needed
	QUERY = """
        SELECT contrib_id, amount
        FROM contrib_legislators JOIN contributors USING (contrib_id)
        WHERE contrib_legislators.leg_id = ? AND contributors.contrib_type = 'I'
        """
	db_cursor.execute(QUERY, (member_choice_id,))

	indiv_contributions = db_cursor.fetchall()
	#PAC info gathering
	QUERY = """
        SELECT contrib_id, amount
        FROM contrib_legislators JOIN contributors USING (contrib_id)
        WHERE contrib_legislators.leg_id = ? AND contributors.contrib_type = 'C'
        """
	db_cursor.execute(QUERY, (member_choice_id,))

	pac_contributions = db_cursor.fetchall()
	
	## populate indiv. & PAC dictionaries with key = contributor ID, value = total given to member 
	indiv_sum = 0.0

	for tup in indiv_contributions:
		indiv_sum += float(tup[1])
		indiv_to_mem_dict[tup[0]] = indiv_to_mem_dict.get(tup[0], 0) + tup[1]
	
	pac_sum = 0.0

	for tup in pac_contributions:
		pac_sum += float(tup[1])
		pac_to_mem_dict[tup[0]] = pac_to_mem_dict.get(tup[0], 0) + tup[1]
	
	## create sorted (by amt given) lists of tuples (id, amt) to get top contributors
	sorted_dict_pac = sorted(pac_to_mem_dict.items(), key=operator.itemgetter(1), reverse=True)
	sorted_dict_indiv = sorted(indiv_to_mem_dict.items(), key=operator.itemgetter(1), reverse=True)
	
	#### Get totals for indiv contributors who give >= $2,000 in one contribution and small contributors (<$2,000)
	sum_large_contrib = 0.0
	sum_small_contrib = 0.0

	for tup in indiv_contributions:
		if float(tup[1]) >= 2000.00:
			sum_large_contrib += float(tup[1])
		else:
			sum_small_contrib += float(tup[1])

	#list of the dictionary key/value pairs for the json tree
	top_ten_indiv_child_list = []
	top_ten_pac_child_list = []

## This method loses title and middle initial
	# for tup in sorted_dict_indiv[:10]:
	# 	contributor = Contributors.query.filter(Contributors.contrib_id == tup[0]).one()
	# 	contrib_name = contributor.name.split(',')
	# 	contrib_last = contrib_name[0]
	# 	contrib_first = contrib_name[1].split(" ")
	# 	contrib_first = contrib_first[1]
	# 	print "second first ", contrib_first
	# 	contrib_name = contrib_first + " " + contrib_last
	# 	contrib_industry = contributor.industry.industry_name
	# 	if contributor.industry:
	# 		top_ten_indiv_child_list.append({"name": contrib_name, "value": 5, "industry": contrib_industry})
	# 	else:
	# 		top_ten_indiv_child_list.append({"name": contrib_name, "value": 5, "industry": "unknown"})

## This method has the names last, first m.i. title

	for tup in sorted_dict_indiv[:10]:
		contributor = Contributors.query.filter(Contributors.contrib_id == tup[0]).one()
		contrib_name = contributor.name
		
		if contributor.industry:
			contrib_industry = contributor.industry.industry_name
			top_ten_indiv_child_list.append({"name": contrib_name, "value": 10, "industry": contrib_industry, "tooltip_text": "A Top 10 Donor:"})
		else:
			top_ten_indiv_child_list.append({"name": contrib_name, "value": 10, "industry": "unknown", "tooltip_text": "A Top 10 Donor:"})

	for tup in sorted_dict_pac[:10]:
		contributor = Contributors.query.filter(Contributors.contrib_id == tup[0]).one()
		contrib_name = contributor.name
		
		if contributor.industry:
			contrib_industry = contributor.industry.industry_name
			top_ten_pac_child_list.append({"name": contrib_name, "value": 10, "industry": contrib_industry, "tooltip_text": "A Top 10 Donor:"})
		else:
			top_ten_pac_child_list.append({"name": contrib_name, "value": 10, "industry": "unknown", "tooltip_text": "A Top 10 Donor:"})


	#### Future: Query for the top individual to PAC and PAC to PAC donations

	
###################################################################
##### Build the dictionary that will become the JSON magic ########
###################################################################
	
### Empty Dictionaries to fill the tree ###
	# Main branch
	contributions = {}

	#sub/children dictionaries for varies branches of tree
	sum_i_contributions = {}
	sum_p_contributions = {}
	large_contrib = {}
	small_contrib = {}


	large_contrib["name"] = "Large Individual Donors"
	large_contrib["children"] = top_ten_indiv_child_list
	large_contrib["value"] = int(100*(sum_large_contrib/(sum_large_contrib+sum_small_contrib)))
	large_contrib["industry"] = "Large"
	large_contrib["tooltip_text"] = "Total Contributions from Large Donors: " '${:,.0f}'.format(sum_large_contrib)
	
	small_contrib["name"] = "Small Individual Donors"
	small_contrib["value"] = int(100*(sum_small_contrib/(sum_large_contrib+sum_small_contrib)))
	small_contrib["industry"] = "Small"
	small_contrib["tooltip_text"] = "Total Contributions from Small Donors: " '${:,.0f}'.format(sum_small_contrib)

	sum_i_contributions["name"] = "Individual Donors"
	sum_i_contributions["children"] = [large_contrib, small_contrib]
	sum_i_contributions["value"] = int(100*(indiv_sum/(indiv_sum + pac_sum)))
	sum_i_contributions["industry"] = "Individuals"
	sum_i_contributions["tooltip_text"] = "Total Contributions from Individuals: " '${:,.0f}'.format(indiv_sum)


	sum_p_contributions["name"] = "Political Action Commitee Donors"
	sum_p_contributions["children"] = top_ten_pac_child_list
	sum_p_contributions["value"] = int(100*(pac_sum/(indiv_sum + pac_sum)))
	sum_p_contributions["industry"] = "PACs"
	sum_p_contributions["tooltip_text"] = "Total Contributions from PACs: " '${:,.0f}'.format(pac_sum)

	contributions["name"] = member
	contributions["children"] = [sum_i_contributions, sum_p_contributions]
	contributions["value"] = 25
	contributions["industry"] = member_obj.party

	return contributions


######################################################################################################################################

def get_first_term_year(leg_id, apikey):
	"""API call to Sunlight Foundation to get the first year a Member of Congress was in elected to Congress 

	takes an id, assigned by Center for Responsive Politics, for the member and returns just the first year """

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