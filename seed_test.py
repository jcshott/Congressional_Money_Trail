###All the data from CRP to the db! 
import requests, os, csv
from model import  connect_to_db, db, Legislator, Contrib_leg, Contributors, Type_contrib, Contrib_pac, Industry
from server import app
from helper_functions import get_first_term_year
from codecs import encode
from string import capwords

#keep track of current legislators so can weed out cont. data we won't use
current_legislator_dict = {}

#to track contributor ids so don't try to add to db more than once
cont_id_dict = {} 

def load_legislators():
    """Take information from Sunlight Fdn csv file; calls to Sunlight API for the first election"""
    #for first year elected. I have a function to do the API call for me, where do I define function?
    #need to figure out how to not hardcode my API key!  Look at Twitter bot

    file_open = open("./src/legislators_test.csv")
   
    for index, line in enumerate(file_open): #enumerate gives tuple of index of line & the line info. use to keep track of where we are & commmit every so often
        if index > 0: #skip first line that is a header
            legislators = line.rstrip().split(",")
            #checks if member is currently in office, 0 means no.

            if int(legislators[9]) == 1:
            
                crp_id = legislators[20]
                current_legislator_dict.setdefault(crp_id, True) #fill current members dict. so can only pull those values in our cont. table

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

                first_elected = get_first_term_year(crp_id, os.environ['SUNLIGHT_API_KEY']) #API call to SLF to get the year
                
                temp_legislator_object = Legislator(leg_id=crp_id, bioguide_id=bioguide_id, first=first, last=last, nickname=nickname, suffix=suffix, 
                                                    title=title, state=state, party=party, chamber=chamber, twitter_id=twitter_id, 
                                                    facebook_id=facebook_id, district=district, sen_rank=sen_rank, off_website=off_website, 
                                                    open_cong_url=open_cong_url, pict_link=pict_link, first_elected=first_elected)

                # object_list = db.session.add(temp_legislator_object)
    return temp_legislator_object