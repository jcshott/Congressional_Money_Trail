###All the data to my DB!  but really just a test set first....

from model import Legislator, Contrib_Leg, Contributors, Type_Contrib, Contrib_PAC, connect_to_db, db
from server import app

def load_legislators():
	"""Take information from Sunlight Fdn csv file; calls to CRP API for the first election"""
	

	file_open = open("src/other_data/legislators.csv")
 
    for line in file_open:
        temp_data = line.rstrip()
        legislators = temp_data.split(",")
		
		if legislators[9] == 0:	#checks the in_office field so only loads members currently in office. 
			continue			#if 0, not in office so skip
		
		else:
			leg_id = legislators[20]
			bioguide_id = legislators[16]
			first = legislators[1]
			last = legislators[3]
			nickname = legislators[5]
			suffix = legislators[4]
			title = legislators[0]
			state = legislators[7]
			party = legislators[6]
			if legislators[0] == "Sen":
				chamber = "Senate"
			else:
				chamber = "House"

			twitter_id = legislators[21]
			facebook_id = legislators[24]
			
			if legislators[0] =="Sen":
				continue
			else:
				district = legislators[8]  #skip if a senator
			off_website = legislators[13]
			open_cong_url = legislators[22]
			
			pict_link = "https://theunitedstates.io/images/congress/225x275/"+legislators[16]+".jpg" #get from webaddress
			
			first_elected =  #get from CRP API call.

			
			temp_legislator_object = Legislator(leg_id=leg_id, bioguide_id=bioguide_id, first=first, last=last, nickname=nickname, suffix=suffix, title=title, state=state, party=party, chamber=chamber, twitter_id=twitter_id, facebook_id=facebook_id, district=district, off_website=off_website, open_cong_url=open_cong_url, pict_link=pict_link)

			db.session.add(temp_legislator_object)

	db.session.commit()


def load_contributions():


if __name__ == "__main__":
    connect_to_db(app)