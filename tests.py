import unittest, os, requests, sqlite3
import server
from server import app
from helper_functions import get_first_term_year, ordered_tuples
from model import connect_to_db, db, Legislator, Contrib_leg, Contributors, Type_contrib, Contrib_pac
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class MyAppUnitTestCase(unittest.TestCase):

    def test_get_first_term_year(self):
        assert(get_first_term_year("N00007335", os.environ['Sunlight_API_Key']) == 1993)

    def test_ordered_tuples(self):
    	assert(ordered_tuples({'MT': 'Montana', 'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska',}) == [('MT', "Montana"), ("NE", "Nebraska"), ("NC", "North Carolina"), ("ND", "North Dakota")])

    def test_create_contribution_dict(self):
        testMember = Legislator.query.filter_by(leg_id  = "N00007335").one()
        assert(testMember.create_contribution_dict() == {'tooltip_text': u'Click through map to see who contributes to Rep. Eshoo', 'industry': u'D', 'name': u'Rep. Eshoo', 'value': 50, 'children': [{'tooltip_text': 'Total Contributions from Individuals: $3,349,515', 'industry': 'Individuals', 'value': 44, 'tooltip_click': 'Click node to see breakdown of large & small donors', 'children': [{'tooltip_text': 'Total Contributions from Large Donors: $1,826,600', 'industry': 'Large', 'value': 54, 'tooltip_click': 'Click to see top 10 individual donors', 'children': [{'industry': u'retired', 'name': u'Codispoti, Fran', 'value': 10, 'tooltip_text': u'Top 10 Donor: $26,600 total donated to Rep. Eshoo'}, {'industry': u'retired', 'name': u'Geschke, Charles', 'value': 10, 'tooltip_text': u'Top 10 Donor: $25,500 total donated to Rep. Eshoo'}, {'industry': u"women's Issues", 'name': u'Yano, Marcella', 'value': 10, 'tooltip_text': u'Top 10 Donor: $24,200 total donated to Rep. Eshoo'}, {'industry': u'real Estate', 'name': u'Marcus, George M', 'value': 10, 'tooltip_text': u'Top 10 Donor: $23,325 total donated to Rep. Eshoo'}, {'industry': u'pharmaceuticals/health Products', 'name': u'Zaffaroni, Alejandro C', 'value': 10, 'tooltip_text': u'Top 10 Donor: $23,300 total donated to Rep. Eshoo'}, {'industry': u'pro-israel', 'name': u'Federman, Irwin', 'value': 10, 'tooltip_text': u'Top 10 Donor: $22,700 total donated to Rep. Eshoo'}, {'industry': u'lawyers/law Firms', 'name': u'Cotchett, Joseph W', 'value': 10, 'tooltip_text': u'Top 10 Donor: $22,000 total donated to Rep. Eshoo'}, {'industry': u'securities & Investment', 'name': u'Freidenrich, Jill', 'value': 10, 'tooltip_text': u'Top 10 Donor: $21,300 total donated to Rep. Eshoo'}, {'industry': u'securities & Investment', 'name': u'Freidenrich, John', 'value': 10, 'tooltip_text': u'Top 10 Donor: $21,300 total donated to Rep. Eshoo'}, {'industry': u'beer', 'name': u'Fox, Michael', 'value': 10, 'tooltip_text': u'Top 10 Donor: $21,200 total donated to Rep. Eshoo'}], 'name': 'Large Individual Donors'}, {'industry': 'Small', 'name': 'Small Individual Donors', 'value': 45, 'tooltip_text': 'Total Contributions from Small Donors: $1,522,915'}], 'name': 'Individual Donors'}, {'tooltip_text': 'Total Contributions from Political Action Committees (PACs): $4,158,583', 'industry': 'PACs', 'value': 55, 'tooltip_click': 'Click node to see top 10 PAC contributors', 'children': [{'industry': u'telecom Services & Equipment', 'name': u'National Cable & Telecommunications Assn', 'value': 10, 'tooltip_text': u'Top 10 Donor: $60,000 total donated to Rep. Eshoo'}, {'industry': u'real Estate', 'name': u'National Assn of Realtors', 'value': 10, 'tooltip_text': u'Top 10 Donor: $56,000 total donated to Rep. Eshoo'}, {'industry': u'securities & Investment', 'name': u'National Venture Capital Assn', 'value': 10, 'tooltip_text': u'Top 10 Donor: $56,000 total donated to Rep. Eshoo'}, {'industry': u'defense Aerospace', 'name': u'Lockheed Martin', 'value': 10, 'tooltip_text': u'Top 10 Donor: $56,000 total donated to Rep. Eshoo'}, {'industry': u'accountants', 'name': u'Ernst & Young', 'value': 10, 'tooltip_text': u'Top 10 Donor: $55,000 total donated to Rep. Eshoo'}, {'industry': u'pharmaceuticals/health Products', 'name': u'Genentech Inc', 'value': 10, 'tooltip_text': u'Top 10 Donor: $54,000 total donated to Rep. Eshoo'}, {'industry': u'pharmaceuticals/health Products', 'name': u'Johnson & Johnson', 'value': 10, 'tooltip_text': u'Top 10 Donor: $51,000 total donated to Rep. Eshoo'}, {'industry': u'building Trade Unions', 'name': u'Plumbers/Pipefitters Union Local 467', 'value': 10, 'tooltip_text': u'Top 10 Donor: $50,000 total donated to Rep. Eshoo'}, {'industry': u'lawyers/law Firms', 'name': u'American Assn for Justice', 'value': 10, 'tooltip_text': u'Top 10 Donor: $49,500 total donated to Rep. Eshoo'}, {'industry': u'industrial Unions', 'name': u'Intl Brotherhood of Electrical Workers', 'value': 10, 'tooltip_text': u'Top 10 Donor: $45,250 total donated to Rep. Eshoo'}], 'name': 'Political Action Commitee Donors'}]})
        self.assertIn("name", testMember.create_contribution_dict().keys())

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
		self.assertIn("http://wwww.twitter.com/RepAnnaEshoo", result.data)


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

    