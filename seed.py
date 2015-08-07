###All the data to my DB!  but really just a test set first....
import requests, os
from model import  connect_to_db, db, Legislator, Contrib_leg, Contributors, Type_contrib, Contrib_pac, Industry
from server import app
from helper_functions import get_first_term_year
from codecs import encode

def load_legislators():
    """Take information from Sunlight Fdn csv file; calls to Sunlight API for the first election"""
    #for first year elected. I have a function to do the API call for me, where do I define function?
    #need to figure out how to not hardcode my API key!  Look at Twitter bot

    file_open = open("./src/other_data/legislators.csv")
   
    for index, line in enumerate(file_open): #enumerate gives tuple of index of line & the line info. use to keep track of where we are & commmit every so often
        if index > 0: #skip first line that is a header
            temp_data = line.rstrip()
            legislators = temp_data.split(",")
            #checks if member is currently in office, 0 means no.
            
            if int(legislators[9]) == 0:
                continue
            
            else:
                crp_id = legislators[20]
                bioguide_id = legislators[16]
                first = legislators[1].decode("UTF-8")
                last = legislators[3].decode("UTF-8")
                nickname = legislators[5].decode("UTF-8")
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
                    sen_rank = legislators[8] #only req. for senators
                    district = None
                else:
                    district = int(legislators[8])  #only for house members
                    sen_rank = None

                off_website = legislators[13]
                open_cong_url = legislators[22]
                
                pict_link = "https://theunitedstates.io/images/congress/225x275/"+legislators[16]+".jpg"

                first_elected = get_first_term_year(crp_id, os.environ['Sunlight_API_Key']) #API call to SLF to get the year
                
                temp_legislator_object = Legislator(leg_id=crp_id, bioguide_id=bioguide_id, first=first, last=last, nickname=nickname, suffix=suffix, 
                                                    title=title, state=state, party=party, chamber=chamber, twitter_id=twitter_id, 
                                                    facebook_id=facebook_id, district=district, sen_rank=sen_rank, off_website=off_website, 
                                                    open_cong_url=open_cong_url, pict_link=pict_link, first_elected=first_elected)


                db.session.add(temp_legislator_object)
                
                #commit every 100 records, but ensures our index (where we are in file) stays the same so we don't start over!
                if index % 100 == 0:
                    print "number of rows committed to db=", index
                    db.session.commit()
    db.session.commit()

def load_industry_types():
    """input industry codes with their associated name into database"""

    file_open = open("./src/other_data/catcodes.csv")
    
    for index, line in enumerate(file_open):
        if index > 0: #skip first line that is a header
            temp_data = line.rstrip()
            industry_info = temp_data.split(",")

            industry_code = industry_info[1]
            industry_name = industry_info[3]

            temp_industry_object = Industry(industry_id=industry_code, industry_name=industry_name)
            db.session.add(temp_industry_object)
    db.session.commit()


def load_contribution_info():

    contributions = line.rstrip().split(',') #can i do this???

    transaction_id = contributions[4]


    temp_contrib_leg_obj
    temp_pac_obj
    temp_type_obj
    temp_contrib_pac_obj


if __name__ == "__main__":
    connect_to_db(app)