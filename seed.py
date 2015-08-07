###All the data to my DB!  but really just a test set first....
import requests, os, csv
from model import  connect_to_db, db, Legislator, Contrib_leg, Contributors, Type_contrib, Contrib_pac, Industry
from server import app
from helper_functions import get_first_term_year
from codecs import encode
from string import capwords

def load_legislators():
    """Take information from Sunlight Fdn csv file; calls to Sunlight API for the first election"""
    #for first year elected. I have a function to do the API call for me, where do I define function?
    #need to figure out how to not hardcode my API key!  Look at Twitter bot

    file_open = open("./src/other_data/legislators.csv")
   
    for index, line in enumerate(file_open): #enumerate gives tuple of index of line & the line info. use to keep track of where we are & commmit every so often
        if index > 0: #skip first line that is a header
            legislators = line.rstrip().split(",")
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
                    print "number of rows processed for db=", index
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
            industry_name = capwords(industry_info[3])

            temp_industry_object = Industry(industry_id=industry_code, industry_name=industry_name)
            db.session.add(temp_industry_object)
    db.session.commit()


def load_contribution_data():
    """load data from all the contributions files into 4 different tables in database:

        First proccesses Contributors & Contributor types (indiv or pac), then adds in the different kinds of contributions: Contrib to legislator and Contrib to PAC

    """

    cont_id_dict = {} #to track contributor ids so don't try to add to db more than once
    type_id_dict = {} #same for contributor type codes

    file_list = ["./src/test_data.csv", "./src/test_data_2.csv"] #make sure we read most recent file first so we get the most recent info on the contributors (like employer) since they are only added once.

    for item in file_list:
        file_open = open(item)

        #because the names have a comma, my indices are getting thrown off. use csv reader.  
        contributions = csv.reader(file_open, skipinitialspace=True)
        
        #csv reader parses each line into a list. so need to index into list
        for index, line in enumerate(contributions):
            if index > 0:
                
                print line
                
                #get info on contributor, incl checking our dict. before adding in case we already have their info & type.
                contrib_id = line[11]

                #the names of the contributors are in all caps in file so this puts it into normal case. has no effect if already ok.
                name = capwords(line[10])
                contrib_type = line[12]

                if line[14]:
                    if line[14] == "NONE":
                        employer = None
                    else:
                        employer = capwords(line[14])
                else:
                    employer = None

                if line[20]:
                    if line[20] == "NONE":
                            industry_id = None
                    else:
                        industry_id = line[20]
                else:
                    industry_id = None

                #need to weed out multiples of the contributor going into table - otherwise fails PK constraint on contributor_id.
                #add the id as a key and set initial value to 1 but increment value every time you have someone with that id.
                cont_id_dict[contrib_id] = cont_id_dict.get(contrib_id, 0) + 1

                #allow for the person to be added to Contributor table first time encountered but not after.
                if cont_id_dict.get(contrib_id) == 1:
                    temp_contrib_obj = Contributors(contrib_id=contrib_id, contrib_type=contrib_type, name=name, employer=employer, industry_id=industry_id)
                    db.session.add(temp_contrib_obj)

                                    
                #weed out multiples of the type-id trying to be committed to table because id is PK
                type_id_dict.setdefault(contrib_type, None)

                type_id_dict["I"] = "Individual"
                type_id_dict["C"] = "PAC"

                type_label = type_id_dict.get(contrib_type, None)
                
                #need to add these once and only once.
                type_id_dict["counter-indiv"] = type_id_dict.get("counter-indiv", 0) + 1
                type_id_dict["counter-pac"] = type_id_dict.get('counter-pac', 0) + 1

                if cont_id_dict.get("counter-indiv") == 1 or type_id_dict.get("counter-pac") == 1:
                    temp_type_obj = Type_contrib(contrib_type=contrib_type, type_label=type_label)
                    db.session.add(temp_type_obj)


                #if to a politician, send info to politician table. else, send to pac cont. table
                if line[28] == "P":
                    # transact_id = line[4] #set up with autoincrement/int. need to change table if want to use FEC info
                    leg_id = line[26]
                    amount = int(float(line[8])) #was getting value error when string had .00
                                        
                    temp_contrib_leg_obj = Contrib_leg(contrib_id=contrib_id, leg_id=leg_id, amount=amount)
                                     
                    db.session.add(temp_contrib_leg_obj)
                
                elif line[28] == "C":
                    # transact_id = line[4] add back if I want to link to FEC info, didn't have in orig table
                    recpt_id = line[26]
                    amount = int(float(line[8]))

                    if line[27]:
                        recpt_party = line[27]
                    else:
                        recpt_party = None
                    
                    temp_contrib_pac_obj = Contrib_pac(contrib_id=contrib_id, recpt_id=recpt_id, amount=amount, rec_party=recpt_party)
                    db.session.add(temp_contrib_pac_obj)


                if index % 5 == 0: #change to 100 for real import
                    db.session.commit()
                    print "number of rows processed for db=", index

    
        db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)