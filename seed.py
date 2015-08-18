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

    file_open = open("./src/legislators.csv")
   
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

                first_elected = get_first_term_year(crp_id, os.environ['Sunlight_API_Key']) #API call to SLF to get the year
                
                temp_legislator_object = Legislator(leg_id=crp_id, bioguide_id=bioguide_id, first=first, last=last, nickname=nickname, suffix=suffix, 
                                                    title=title, state=state, party=party, chamber=chamber, twitter_id=twitter_id, 
                                                    facebook_id=facebook_id, district=district, sen_rank=sen_rank, off_website=off_website, 
                                                    open_cong_url=open_cong_url, pict_link=pict_link, first_elected=first_elected)


                db.session.add(temp_legislator_object)
                
                #commit every 100 records, but ensures our index (where we are in file) stays the same so we don't start over!
                if index % 100 == 0:
                    print "number of legislative rows processed for db=", index
                    db.session.commit()

    db.session.commit()

def load_industry_types():
    """input industry codes with their associated name into database"""

    file_open = open("./src/catcodes.csv")
    
    for index, line in enumerate(file_open):
        if index > 0: #skip first line that is a header
            temp_data = line.rstrip()
            industry_info = temp_data.split(",")

            industry_code = industry_info[1].strip('"')
            industry_name = capwords(industry_info[3]).strip('"')

            temp_industry_object = Industry(industry_id=industry_code, industry_name=industry_name)
            db.session.add(temp_industry_object)
    db.session.commit()


def load_indiv_contribution_data():
    """load data from all the individual files to the contribution to legislators table, contributors table, and contributor type table

        parses the CRP data from "indivs" files for each cycle. currently only going back to 2004.
    """

    #make sure we read most recent file first so we get the most recent info on the contributors (like employer) since they are only added once.
    file_list = ["./src/individuals/indivs14.txt", "./src/individuals/indivs12.txt", "./src/individuals/indivs10.txt", "./src/individuals/indivs08.txt", "./src/individuals/indivs06.txt", "./src/individuals/indivs04.txt"] 
    for file_path in file_list:
        file_open = open(file_path)
        
        for index, line in enumerate(file_open):
            value = line.split("|,|")
            if value[4] in current_legislator_dict:
                # per CRP documentation. to make sure only get indiv. donors, check that contrib_id has a value. first need to strip whitespace.
                # this worked on the test set but not when running the full thing, non-I-contributors still got in. unsure why. so, just deleted 
                # from db directly by deleting all from contrib_legislators table where id was 11-spaces long.
                value[2].replace(" ", "")
                if value[2] != ' ':
                    contrib_id = value[2].strip()
                    FEC_trans_id = value[1]
                    name = capwords(value[3])
                    contrib_type = "I"
                    contrib_state = value[9]
                    cycle = value[0].strip('|')
                    leg_id = value[4]

                    #first split of line makes it so there is one grouping of industry, data & amount given so need to further parse that.
                    split_ind_amt_data = value[7].split(',')
                    if split_ind_amt_data[0]:
                        if split_ind_amt_data[0] == "NONE":
                                industry_id = None
                        else:
                            industry_id = split_ind_amt_data[0].strip('|')
                    else:
                        industry_id = None

                    amount = int(float(split_ind_amt_data[2]))

                    # need to weed out multiples of the contributor going into table - otherwise fails PK constraint on contributor_id.
                    # add the id as a key and set initial value to 1 but increment value every time you have someone with that id.
                    cont_id_dict[contrib_id] = cont_id_dict.get(contrib_id, 0) + 1

                    
                    if industry_id[0:2] != "Z9":
                    #allow for the person to be added to Contributor table first time encountered but not after.
                        if cont_id_dict.get(contrib_id) == 1:
                            temp_contrib_obj = Contributors(contrib_id=contrib_id, name=name, contrib_type=contrib_type, industry_id=industry_id, contrib_state=contrib_state)

                            db.session.add(temp_contrib_obj)

                        temp_contrib_leg_obj = Contrib_leg(contrib_id=contrib_id, FEC_trans_id=FEC_trans_id, leg_id=leg_id, amount=amount, cycle=cycle)
                        db.session.add(temp_contrib_leg_obj)

                        if index % 100 == 0:
                            print "rows of indiv data: ", index
                            db.session.commit()
            
            db.session.commit()


def load_pac_to_leg_contribution_data():
    """load data from all the contributions files into 4 different tables in database:

        First proccesses Contributors & Contributor types (indiv or pac), then adds in the different kinds of contributions: Contrib to legislator and Contrib to PAC
    """
    
    file_list = ["./src/pac_to_cand/pacs14.txt", "./src/pac_to_cand/pacs12.txt", "./src/pac_to_cand/pacs10.txt", "./src/pac_to_cand/pacs08.txt", "./src/pac_to_cand/pacs06.txt", "./src/pac_to_cand/pacs04.txt"] 

    for file_path in file_list:
        file_open = open(file_path)
        
        for index, line in enumerate(file_open):
            value = line.split(",")
            leg_id = value[3].strip('|')

            if leg_id in current_legislator_dict:
                cont_type = value[7].strip('|')
                industry_id = value[6].strip('|')
                #z9 and z4 are considered non-contribution types -> transfers
                if industry_id[0:2] != "z9" and industry_id[0:2] != "z4":
                    if cont_type != "24A" and value[7] != "24N":
                        cycle = value[0].strip('|')
                        FEC_trans_id = value[1].strip('|')
                        contrib_id = value[2].strip('|')
                        amount = int(float(value[4]))
                        
                        temp_contrib_leg_obj = Contrib_leg(contrib_id=contrib_id, FEC_trans_id=FEC_trans_id, leg_id=leg_id, amount=amount, cycle=cycle)
                        db.session.add(temp_contrib_leg_obj)  

                        if index % 100 == 0:
                            print "rows of pac data: ", index
                            db.session.commit()

        db.session.commit()             


def load_pac_contributors():
    """ load details on pact contributors into db from committee files"""

    file_list = ["./src/pac_info/cmtes14.txt", "./src/pac_info/cmtes12.txt", "./src/pac_info/cmtes10.txt","./src/pac_info/cmtes08.txt", "./src/pac_info/cmtes06.txt", "./src/pac_info/cmtes04.txt"] 

    for file_path in file_list:
        file_open = open(file_path)
       
        for index, line in enumerate(file_open):
            value = line.split(",")
            contrib_id = value[1].strip('|')      
            contrib_type = "C"

            print "preloop: ", contrib_id
            #check if contributor has been entered by checking dictionary of those already in db
            if contrib_id not in cont_id_dict:
                cont_id_dict.setdefault(contrib_id, True)
                print "post-loop: ", contrib_id
                name = value[2].strip('|')

                if value[9]:
                    industry_id = value[9].strip("|")

                temp_contrib_obj = Contributors(contrib_id=contrib_id, industry_id=industry_id, name=name, contrib_type=contrib_type)
                print "successful addition on line: ", index
                db.session.add(temp_contrib_obj)
                print "successful commit on line: ", index


            if index % 100 == 0:
                db.session.commit()
                print "number of rows processed: ", index
        
        db.session.commit()
                                    


if __name__ == "__main__":
    connect_to_db(app)

    load_legislators()
    load_industry_types()
    load_indiv_contribution_data()
    load_pac_to_leg_contribution_data()
    load_pac_contributors()