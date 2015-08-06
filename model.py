"""Models and database functions"""

from flask_sqlalchemy import SQLAlchemy

#Create connection to database

db = SQLAlchemy()

####################################################################
#Model definitions

class Legislator(db.Model):
	"""Members of Congress
		data from Sunlight Foundation CongressAPI
	"""

	__tablename__='legislators'

	leg_id = db.Column(db.String(50), primary_key=True) #unique ID given by Ctr for Responsive Politics
	bioguide_id = db.Column(db.String(8)) #need for getting picture
	first = db.Column(db.String(30))
	last = db.Column(db.String(50))
	nickname = db.Column(db.String(20), nullable=True)
	suffix = db.Column(db.String(5), nullable=True)
	title = db.Column(db.String(3))
	state = db.Column(db.String(2))
	district = db.Column(db.Integer, nullable=True) #skip if a senator
	party = db.Column(db.String(1))
	chamber = db.Column(db.String(10))
	twitter_id = db.Column(db.String(20), nullable=True)
	facebook_id = db.Column(Integer, nullable=True)
	pict_link = db.Column(String(100)) #get from webaddress
	off_website = db.Column(String(100)) 
	open_cong_url = db.Column(String(100), nullable=True)
	first_elected = db.Column(String(4)) #get from CRP

	def __repr__(self):
        """Prints actual useful information about the legislator instead of its memory location"""

    	return "<Legislator mem_id=%s: first=%s last=%s, state=%s>" % (self.leg_id, self.first, self.last, self.state)


class Contrib_Leg(db.Model):
	"""data on contributions to Members of Congress"""

	__tablename__ = 'contrib_legislators'

	transact_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	contrib_id = db.Column(db.String(50), db.ForeignKey('contributors.contrib_id')) #ID of who made contribution
	leg_id = db.Column(db.String(50), db.ForeignKey('legislators.leg_id')) #ID of who gets contribution
	amount = db.Column(db.Integer)
	
	contributor = db.relationship("Contributors", backref=db.backref("contrib_legislators", order_by=amount))
	legislator = db.relationship("Legislator", backref=db.backref("contrib_legislators", order_by=amount))


	def __repr__(self):
        """Prints actual useful information about the contribution transaction instead of its memory location"""

    	return "<Contributor ID=%s, Reciever ID=%s, Amount=%s>" % (self.contrib_id, self.mem_id, self.amount)


class Contributors(db.Model):
	"""Details on contributing entities

		Indivduals (indicated by 'I')
		Political Action Committees (PACs) (indicated by 'C')

	"""

	__tablename__='contributors'

	contrib_id = db.Column(db.String(50), primary_key=True)
	contrib_type = db.Column(db.String(2), db.ForeignKey('contributor_type.contrib_type'))
	name = db.Column(db.String(100))
	industry = db.Column(db.String(50))
	employer = db.Column(db.String(50), nullable=True)
	industry = db.Column(db.String(50), nullable=True)

	contrib_type = db.relationship("Type_Contrib", backref=db.backref("contributors"))


	def __repr__(self):
        """Prints actual useful information about the contributor instead of its memory location"""

    	return "<Contributor Name=%s, Type=%s, ID=%s>" % (self.name, self.contrib_type, self.contrib_id)


class Type_Contrib(db.Model):
	"""Details on what contributor types there are. I for Indivdual; C for PACs 
	leaving room for more than just indiv. and pac in the future
	"""

	__tablename__='contributor_types'

	contrib_type = db.Column(db.String(2), primary_key=True)
	type_label = db.Column(db.String(50))

	def __repr__(self):
	        """Prints actual useful information about the type instead of its memory location"""

	    return "<Type ID=%s, Label=%s>" % (self.contrib_type, self.type_label)


class Contrib_PAC(db.Model):
	"""tracking contributions to PACs
	can be PAC-to-PAC or Individual-to-PAC
	"""

	__tablename__='contrib_pacs'

	transact_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	contrib_id = db.Column(db.String(50), db.ForeignKey('contributors.contrib_id')) #ID of who made contribution
	recpt_id = db.Column(db.String(50)) #ID of who gets contribution
	amount = db.Column(db.Integer)

	contributor = db.relationship("Contributors", backref=db.backref("contrib_pacs", order_by=amount))
	
	
	def __repr__(self):
	        """Prints actual useful information about the contribution to PACs instead of its memory location"""

		return "<Contributor ID=%s, Recipient ID=%s, Amount=%s>" % (self.contrib_id, self.recpt_id, self.amount)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contributions.db'
    db.app = app
    db.init_app(app)



if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."

