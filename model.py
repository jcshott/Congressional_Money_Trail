"""Models and database functions"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.sql import label
from sqlalchemy.dialects.postgresql import JSON
import requests, os, operator
import psycopg2

#Create connection to database

db = SQLAlchemy()

db_connection = psycopg2.connect("dbname='contributions' user='coreyshott' host='localhost'")
db_cursor = db_connection.cursor()

####################################################################
#Model definitions

class Legislator(db.Model):
	"""Members of Congress
		data from Sunlight Foundation CongressAPI
	"""

	__tablename__='legislators'

	leg_id = db.Column(db.String(50), primary_key=True) #unique ID given by Ctr for Responsive Politics
	bioguide_id = db.Column(db.String(8), nullable=False) #need for getting picture
	first = db.Column(db.String(30), nullable=False)
	last = db.Column(db.String(50), nullable=False)
	nickname = db.Column(db.String(20), nullable=True)
	suffix = db.Column(db.String(5), nullable=True)
	title = db.Column(db.String(3), nullable=False)
	state = db.Column(db.String(2), nullable=False)
	district = db.Column(db.Integer, nullable=True) #skip if a senator
	sen_rank = db.Column(db.String(15), nullable=True) #Sr. or Jr. status of Senator
	party = db.Column(db.String(3), nullable=False)
	chamber = db.Column(db.String(10), nullable=False)
	twitter_id = db.Column(db.String(20), nullable=True)
	facebook_id = db.Column(db.String(50), nullable=True)
	pict_link = db.Column(db.String(100)) #get from webaddress
	off_website = db.Column(db.String(100), nullable=True) 
	open_cong_url = db.Column(db.String(100), nullable=True)
	first_elected = db.Column(db.Integer) #get from SLF call
	top_contributors = db.Column(JSON, nullable=True)

	def __repr__(self):
		"""prints useful info on legislator"""

		return "<Legislator mem_id=%s: first=%s last=%s, state=%s>" % (self.leg_id, self.first, self.last, self.state)

	def serialize(self):
		"""function so I can change the returned object from a query into a JSON object to show in my DOM"""

		return {
		    'leg_id': self.leg_id,
		    'first': self.first,
		    'last': self.last,
		    'nickname': self.nickname,
		    'suffix': self.suffix,
		    'title': self.title,
		    'state': self.state,
		    'district': self.district,
		    'sen_rank': self.sen_rank,
		    'party': self.party,
		    'chamber': self.chamber,
		    'twitter_id': self.twitter_id,
		    'facebook_id': self.facebook_id,
		    'pict_link': self.pict_link,
		    'off_website': self.off_website,
		    'open_cong_url': self.open_cong_url,
		    'first_elected': self.first_elected
		    }

	def create_contribution_dict(self):
		"""Create a dictionary from my database data that is selected based on user input

		takes in the instance of a selected Member of Congress (that is identified from the user, instantiated on server side)
		returns a dictionary that can be jsonified

		"""

	###################################################################
	## Queries and data analysis that goes into the branches #####
	###################################################################

		#take in selected member id, get member object from db and extract information to be displayed on node in browser.
		member = "%s. %s" % (self.title, self.last)
			
		## use dictionaries to store how much each indiv person/pac gives to the member then can sort and get top contributors
		indiv_to_mem_dict = {}
		pac_to_mem_dict = {}

		### Get ID and amount donated to Member of Congress for Indiv. & PACs. will use to calculate other info needed
		QUERY = """
	        SELECT contrib_id, amount
	        FROM contrib_legislators JOIN contributors USING (contrib_id)
	        WHERE contrib_legislators.leg_id = %s AND contributors.contrib_type ='I'
	        """
		db_cursor.execute(QUERY, (self.leg_id,))

		indiv_contributions = db_cursor.fetchall()
		#PAC info gathering
		QUERY = """
	        SELECT contrib_id, amount
	        FROM contrib_legislators JOIN contributors USING (contrib_id)
	        WHERE contrib_legislators.leg_id = %s AND contributors.contrib_type ='C'
	        """
		db_cursor.execute(QUERY, (self.leg_id,))

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

	## This method has the names last, first m.i. title

		for tup in sorted_dict_indiv[:10]:
			contributor = Contributors.query.filter(Contributors.contrib_id == tup[0]).one()
			contrib_name = contributor.name
			contrib_total = tup[1]
			
			if contributor.industry_id:
				contrib_industry = contributor.industry_id
				top_ten_indiv_child_list.append({"name": contrib_name, "value": 10, "industry": contrib_industry, "tooltip_text": "Top 10 Indiv. Donor: %s total donated to %s. %s" % ('${:,.0f}'.format(contrib_total), self.title, self.last), "type": "indiv", "member_party": self.party})
			else:
				top_ten_indiv_child_list.append({"name": contrib_name, "value": 10, "industry": "unknown", "tooltip_text": "Top 10 Indiv. Donor: %s total donated to %s. %s" % ('${:,.0f}'.format(contrib_total), self.title, self.last), "type": "indiv", "member_party": self.party})

		for tup in sorted_dict_pac[:10]:
			contributor = Contributors.query.filter(Contributors.contrib_id == tup[0]).one()
			contrib_name = contributor.name
			contrib_total = tup[1]

			if contributor.industry_id:
				contrib_industry = contributor.industry_id
				top_ten_pac_child_list.append({"name": contrib_name, "value": 10, "industry": contrib_industry, "tooltip_text": "Top 10 PAC Donor: %s total donated to %s. %s" % ('${:,.0f}'.format(contrib_total), self.title, self.last), "type": "PAC", "member_party": self.party})
			else:
				top_ten_pac_child_list.append({"name": contrib_name, "value": 10, "industry": "unknown", "tooltip_text": "Top 10 PAC Donor: %s total donated to %s. %s" % ('${:,.0f}'.format(contrib_total), self.title, self.last), "type": "PAC", "member_party": self.party})


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
		large_contrib["tooltip_click"] = "Click to see top 10 individual donors"
		large_contrib["tooltip_text"] = "Total Contributions from Large Donors: %s" % ('${:,.0f}'.format(sum_large_contrib))
		large_contrib["member_party"] = self.party
		
		small_contrib["name"] = "Small Individual Donors"
		small_contrib["value"] = int(100*(sum_small_contrib/(sum_large_contrib+sum_small_contrib)))
		small_contrib["industry"] = "Small"
		small_contrib["tooltip_text"] = "Total Contributions from Small Donors: " '${:,.0f}'.format(sum_small_contrib)
		small_contrib["member_party"] = self.party

		sum_i_contributions["name"] = "Individual Donors"
		sum_i_contributions["children"] = [large_contrib, small_contrib]
		sum_i_contributions["value"] = int(100*(indiv_sum/(indiv_sum + pac_sum)))
		sum_i_contributions["industry"] = "Individuals"
		sum_i_contributions["tooltip_click"] = "Click node to see breakdown of large & small donors"
		sum_i_contributions["tooltip_text"] = "Total Contributions from Individuals: %s" % ('${:,.0f}'.format(indiv_sum))
		sum_i_contributions["member_party"] = self.party


		sum_p_contributions["name"] = "Political Action Commitee Donors"
		sum_p_contributions["children"] = top_ten_pac_child_list
		sum_p_contributions["value"] = int(100*(pac_sum/(indiv_sum + pac_sum)))
		sum_p_contributions["industry"] = "PACs"
		sum_p_contributions["tooltip_click"] = "Click node to see top 10 PAC contributors"
		sum_p_contributions["tooltip_text"] = "Total Contributions from Political Action Committees (PACs): %s" % ('${:,.0f}'.format(pac_sum))
		sum_p_contributions["member_party"] = self.party

		contributions["name"] = member
		contributions["children"] = [sum_i_contributions, sum_p_contributions]
		contributions["value"] = 50
		contributions["industry"] = self.party
		contributions["member_party"] = self.party

		if self.party == "D":
			contributions["tooltip_click"] = "Click through map to see who contributes to %s. %s (Democrat)" % (self.title, self.last)
		if self.party == "R":
			contributions["tooltip_click"] = "Click through map to see who contributes to %s. %s (Republican)" % (self.title, self.last)
		if self.party == "I" or self.party == None:
			contributions["tooltip_click"] = "Click through map to see who contributes to %s. %s (Independent)" % (self.title, self.last)

		return contributions




class Contrib_leg(db.Model):
	"""data on contributions to Members of Congress
		From Center for Responsive Politics
	"""

	__tablename__ = 'contrib_legislators'

	transact_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	FEC_trans_id = db.Column(db.String(20), nullable=False) #only unique within cycle
	# contrib_id = db.Column(db.String(15), db.ForeignKey('contributors.contrib_id'), nullable=False) #ID of who made contribution
	contrib_id = db.Column(db.String(15), nullable=False)
	# leg_id = db.Column(db.String(10), db.ForeignKey('legislators.leg_id'), nullable=False) #ID of who gets contribution
	
	# had problems when experimenting moving to postgres. turned off FK, but caused other problems.
	leg_id = db.Column(db.String(10), nullable=False) 
	amount = db.Column(db.Integer, nullable=False)
	cycle = db.Column(db.Integer)
	
	# contributor = db.relationship("Contributors", backref=db.backref('contrib_legislators', order_by=amount))
	# legislator = db.relationship("Legislator", backref=db.backref('contrib_legislators', order_by=amount))
	

	def __repr__(self):
		return "<Contributor ID=%s, Reciever ID=%s, Amount=%s>" % (self.contrib_id, self.leg_id, self.amount)


class Contributors(db.Model):
	"""Details on contributing entities

		Indivduals (indicated by 'I')
		Political Action Committees (PACs) (indicated by 'C')

	"""
	__tablename__='contributors'

	contrib_id = db.Column(db.String(15), primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	contrib_state = db.Column(db.String(2), nullable=True)
	contrib_type = db.Column(db.String(2), db.ForeignKey('contributor_types.contrib_type'), nullable=False)
	# industry_id = db.Column(db.String(50), db.ForeignKey('industry.industry_id'), nullable=True)
	
	# had problems when moving to postgres, so turned off FK for seeding db. then manually reinstate.
	industry_id = db.Column(db.String(50), nullable=True)
	contrib_type = db.Column(db.String(2), nullable=False)
	# industry = db.relationship('Industry', backref=db.backref('contributors'))
	# cont_type = db.relationship('Type_contrib', backref=db.backref('contributors'))


	def __repr__(self):
		return "<Contributor Name=%s, Type=%s, ID=%s>" % (self.name, self.contrib_type, self.contrib_id)

	def get_top_indiv_to_pac(self):
		""" Get contributions to PACs 
		for a given PAC id, returns top 10 individual contributors to that pac from the contrib_pac table"""

		indiv_to_pac_dict = {}

		QUERY = """
		SELECT contrib_pacs.amount, contributors.name
		FROM contrib_pacs JOIN contributors USING (contrib_id)
		WHERE contrib_pacs.recpt_id = %s AND contributors.contrib_type = 'I'
		"""
		db_cursor.execute(QUERY, (self.contrib_id,))

		indiv_to_pac_cont = db_cursor.fetchall()
		
		indiv_to_pac_sum = 0

		#fills dictionary of all individual contributors to a PAC with name: amount given.
		for item in indiv_to_pac_cont:
			indiv_to_pac_sum += float(item[0])
			indiv_to_pac_dict[item[1]] = indiv_to_pac_dict.get(item[1], 0) + item[0]

		#sort our indiv. contributors by amount given most -> least
		sorted_indiv2pac = sorted(indiv_to_pac_dict.items(), key=operator.itemgetter(0), reverse=True)

		#return list of 10 tuples: contributor name and amount given
		return sorted_pac2pac[:10]

	def get_top_pac_to_pac(self):
		""" Get contributions to PACs 
		for a given PAC id, returns top 10 PAC contributors to that pac from the contrib_pac table"""

		pac_to_pac_dict = {}
	
		QUERY = """
        SELECT contrib_pacs.amount, contributors.name
        FROM contrib_pacs JOIN contributors USING (contrib_id)
        WHERE contrib_pacs.recpt_id = %s AND contributors.contrib_type = 'C'
        """
		db_cursor.execute(QUERY, (self.contrib_id,))

		pac_to_pac_cont = db_cursor.fetchall()
		
		pac_to_pac_sum = 0

		#fills dictionary of all PAC contributors to a PAC with name: amount given.
		for item in pac_to_pac_cont:
			pac_to_pac_sum += float(item[0])
			pac_to_pac_dict[item[1]] = pac_to_pac_dict.get(item[0], 0) + item[0]

		#sort our PAC contributors by amount given most -> least
		sorted_pac2pac = sorted(pac_to_pac_dict.items(), key=operator.itemgetter(0), reverse=True)

		#return list of 10 tuples: contributor name and amount given
		return sorted_pac2pac[:10]

class Type_contrib(db.Model):
	"""Details on what contributor types there are. I for Indivdual; C for PACs 
	leaving room for more than just indiv. and pac in the futures
	"""

	__tablename__='contributor_types'

	contrib_type = db.Column(db.String(2), primary_key=True)
	type_label = db.Column(db.String(50))

	def __repr__(self):
		return "<Type ID=%s, Label=%s>" % (self.contrib_type, self.type_label)

### Holding on seeding this given had to change data source mid-project. leaving out reduces complexity for now.
class Contrib_pac(db.Model):
	"""tracking contributions to PACs, can be PAC-to-PAC or Individual-to-PAC

	shows who made contribution (contrib_id); who recieved $ (recpt_id) and the party affiliation (if applicable) of Reciever (rec_party)
	"""

	__tablename__='contrib_pacs'

	transact_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	contrib_id = db.Column(db.String(50), nullable=False)
	recpt_id = db.Column(db.String(50)) #ID of who gets contribution
	amount = db.Column(db.Integer, nullable=False)
	rec_party = db.Column(db.String(3), nullable=True)
	cycle = db.Column(db.Integer)
	
	def __repr__(self):
		return "<Contributor ID=%s, Recipient ID=%s, Amount=%s>" % (self.contrib_id, self.recpt_id, self.amount)

class Industry(db.Model):
	"""for decoding industry codes in contributors table """

	__tablename__='industry'

	industry_id = db.Column(db.String(10), primary_key=True)
	industry_name = db.Column(db.String(100))

	def __repr__(self):
		return "<Ind Name = %s, ID = %s>" % (self.industry_name, self.industry_id)

##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use postgresql database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://coreyshott@localhost:5432/contributions'
    db.app = app
    db.init_app(app)



if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."

