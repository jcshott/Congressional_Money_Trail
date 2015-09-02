Congressional Money Trail
====================================
Learn more about the developer on [LinkedIn] (www.linkedin.com/in/coreyshott/) and find the project on [GitHub] (www.github.com/jcshott).

Campaign contributions to our federal officials are publicly disclosed but rarely easy to access. Utilizing the past decade of campaign contribution data, Congressional Money Trail seeks to help the public better understand from where their federal congressional representatives receive their campaign money. Just select a state or find a Member of Congress by address and a visual representation of how they finance their campaigns is revealed.

## Features ##

*Current*

- [x] Campaign Contribution data (pipe and comma separated format) from Opensecrets.org imported into SQLite Database
- [x] SQLAlchemy and raw SQL queries database for total campaign contributions to a user-selected Member of Congress.
- [x] Flask-Python server sends JSON object to DOM.

- [x] Result rendered as a tree-diagram graph (d3.js)
- [x] Flask app renders HTML, Jinja2 and handles AJAX requests to the database
- [x] Option to find a Member of Congress by state 
- [x] Option to search for Congressional delegation by address (Google GeocodeAPI and Sunlight Foundation CongressAPI)
- [x] Nodes are sized based on proportion of contributions from identified category as compared to whole

- [x] Summary of campaign contributions from particular category or entity as  mouseover tooltips

*Future*

- [ ] Color lines/nodes according to industry of contributor
- [ ] Capture image to share on social media
- [ ] Extend data to include contributions to top PACs

Below is an example of a full visualization.  Examples of other stages of the app at the end of the document.

![main_screenshot](/static/img/main_ss.png)


##Technology

Python, Flask, SQLite, SQLAlchemy ORM, D3.js, jQuery, JS,  AJAX, HTML, CSS, Sunlight Foundation CongressAPI, Google Geocode API

Dependencies are listed in requirements.txt.  

To run the seed file and use the find congressional delegation by address function, you need both a GoogleMaps API key and Sunlight Foundation API key (both free).

##Backend and Database

Python runs the backend of Congressional Money Trail.  Given the amount of data and speed necessary to deliver information to the DOM, queries are done in both SQLAlchemy and raw SQL with indices added to the database to further increase querying speed.  In addition much of the information and calculations needed to form the JSON object for the D3 visualization are pushed to Python rather than multiple queries.



##Frontend

The front-end is composed  using HTML, custom CSS combined with Bootstrap.  Interactivity with the components are programmed with D3.js,  jQuery, and AJAX.  

D3.js was chosen for the visualization technology because of its prevalence in the data visualization realm and strong documentation.  

##File Guide
* <kbd>model.py</kbd>  Creates the database
* <kbd>seed.py</kbd>  Seeds the database from source files
* <kbd>server.py</kbd> Controls the flask app 
* <kbd>TrailMapTree.js</kbd>  Handles the D3.js visualization rendering
* <kbd>get_members.js</kbd> Handles retrieving data on Congressional Delegations from database either via select-by-state option or select-by-address option.

##Installation

```sh
$ git clone [git-repo-url]
$ virtualenv env
$ pip install -r requirements.txt
```

Download datasets and save to a src subdirectory in project directory:

- Contribution data must be downloaded from [OpenSecrets.org] (http://www.opensecrets.org/myos/bulk.php)  (free account required).

- Legislator information from [Sunlight Foundation] (https://sunlightlabs.github.io/congress/#legislator-spreadsheet)

At the command line:

```sh
$ python -i model.py 
$ db.create_all()
```
...then run

```sh
$ python seed.py
 ```
To start server:
 
```sh
$ python server.py
```


##Additional Screenshots
**Homepage**

![homepage_screenshot](/static/img/homepage_ss.png)

**Example of tooltip and view of individual donor branch**
![indiv_donors_screenshot](/static/img/indiv_donors_ss.png)

**Search by address results**
![search_address_screenshot](/static/img/choose_by_address_ss.png)

**Location for user on information used for the site**
![infobar_screenshot](/static/img/info_bar_ss.png)


**Additional Full Visualization**
![repub_screenshot](/static/img/repub_full_ss.png)
