import requests
import os

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