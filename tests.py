import unittest, os, requests, sqlite3
import server
from server import app
from helper_functions import get_first_term_year, ordered_tuples
from model import connect_to_db, db, Legislator, Contrib_leg, Contributors, Type_contrib, Contrib_pac
from flask_sqlalchemy import SQLAlchemy
from seed_test import load_legislators

db = SQLAlchemy()


class MyAppUnitTestCase(unittest.TestCase):

    def test_get_first_term_year(self):
        assert(get_first_term_year("N00007335", os.environ['SUNLIGHT_API_KEY']) == 1993)

    def test_ordered_tuples(self):
    	assert(ordered_tuples({'MT': 'Montana', 'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska',}) == [('MT', "Montana"), ("NE", "Nebraska"), ("NC", "North Carolina"), ("ND", "North Dakota")])

    def test_create_contribution_dict(self):
        testMember = Legislator.query.filter_by(leg_id  = "N00007335").one()
        self.assertIn("name", testMember.create_contribution_dict().keys())

    # def test_load_legislators(self):
    #     self.assertIsInstance(load_legislators(), Legislator)

class MyAppIntegrationTest(unittest.TestCase):

	def setUp(self):
		print "(setUp ran)"
		self.client = server.app.test_client()

	def test_home(self):
		test_client = server.app.test_client()
		result = test_client.get('/')

		self.assertEqual(result.status_code, 200)
		self.assertIn('Visualize Where Your Federal', result.data)

   
	def test_get_by_address(self):
		test_client = server.app.test_client()
		result = test_client.post('/trail_map', data={"member": "N00007335"})
		self.assertIn("https://theunitedstates.io/images/congress/225x275/E000215.jpg", result.data)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contributions.db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    
    connect_to_db(app)
    
    with app.app_context():
        unittest.main()
    
    print "Connected to DB."

    