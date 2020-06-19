# Airbnb Simulator
This project simulate the basic operation of how the Airbnb works. It allows different customers (host and visitor) to 
search, modify and add new information to the database via our UI. We want to perform all the rental information around 
Boston area to give users a better access to make reservation and posting house.

## Description
This program provides the basic functions for both hosts and visitors. Both hosts and visitors starts within the same 
entry point. Two view is very different with small overlap. Host cannot make any reservation and visitors can not make
any changes on the listings. It requires customer to choose the identity to login in and provide their id number. For 
hosts, it can add new listing, modify own listings. For visitors, they can browse all listings to choose their desired 
house and time to make reservation. For the sake of both hosts and visitors, all the required field starts from a 
star(*) symbol.

## To Start
1. To see the host perspective, click `Host Login`, then enter `8229` for host account and leave password empty to 
`Login` for demo. You can also create your own hid or account (must be unique).
2. You will see 6 different listing in this page. These are all the host `8229` owned. You can click `Add`  to add new 
listing. It will asks you provide some information in order to create your new listing. You can choose any listing to 
delete or modify as well.  You can click `My Profile` to see the detail of the personal information and make some 
changes by clicking `Update` if you wish. For information details, please see *Rental Space (Host View)*.
3. To see the customer(visitor) perspective, back to main page and click `Customer Login`, then enter `1` as cid and 
leave password empty to `Login`. You can also create your own sid by clicking `Sign Up`.
4. Once you login, you can see all the posted listing. You can choose any one you want to see more detailed information 
by choose a listing and click `More Info`. It will lead you to a new window that show all the information about your
choice. 
5. Then you can click `Availability Check` to check the availability of the house; `Reserve` to make actual reservation
to this house, this would you to provide some basic information.
6. When you back to customer page, you can also click `My Profile` to view your personal information and make some 
changes by clicking `Update`; `My Reservation` to see reservation you make and modify it. 
7. For data visualization, back to main page(the start page). Click `Data Visualization` and choose what information
you want to see. It will pop up a web page to show the plot. There are four different type of plots. For more 
information about the plots, see section *Data Visualization*.
8. About page is just for present the information of group members. 
9. `Exit` button is to exit the program. 

## Host Perspective
As a host, it need to provide their hid (host id) in order to login and **no password required**. Once he login, he can 
only see the listings he owned. 

### Host Sign Up Page
Host need to provide basic information in order to make a new account. The information need to provided lists below:
* hid: host id. It allows host to customize his own id. But it need to be unique to distinguish other's uid. Each user
have one unique uid. **It cannot be empty.**
* hurl: host url. It can be empty and program does not check if it is a valid url.
* hname: host name. It can be empty.
* hsince: time when create this account assigned by system. It can not be modified. 
* is_superhost: a boolean value represents whether it is a super host. It allows users to change these value. But **it 
cannot be empty**. 0 represents it is not a super host, otherwise, 1 represents it is a super host. 
* hpic: host picture. It can be empty and program does not check if it is a valid url.
* is_verified: a boolean value represents whether the host has verified this account. It allows users to change these 
value. But **it cannot be empty**. 0 represents this account has not been verified, otherwise, 1 represents it has been
verified.

### Rental Space (Host View)
He can see all his listings as well as make changes to these listings. Also, he can click `My Profile` to see his 
personal information and click `Update` to modify his information. For listings, he can choose one listing and click 
`Modify` to change the information for the particular house, or click `Delete` to delete this listing. In addition, 
he can make a new listing by clicking `Add` Button. For the fields that shows in modifying and adding page. *sid, city,
state, country* are not allowed to be modified. Reason states below:

* sid: unique identifier of a house (rental_space). 
* city, state, country: we only allowed to post listings around Boston area, so, these fields are not allowed to be 
changed.

Fields that allowed to be **emtpy** string:
* surl: url of this rental space. Program does not check if it is a valid url.
* title: the title of this house that host want to show first. 
* rdescription: description of this house. 
* neighborhood_overview
* spic: picture of this house (url). Program does not check if it is a valid url.
* neighborhood

Fields that **cannot be empty**:
* sid: id
* bath_num: number of bathroom that this house has. It can only be integer.
* bed_num: number of bedroom that this house has. It can only be integer.
* rate: rate of this room range from 0 to 100. 
* rtype: room type (can only be 'Entire home/apt', 'Hotel room', 'Private room', 'Shared room')
* ptype: property type (can only be 'Apartment', 'Barn', 'Bed and breakfast', 'Boat', 'Boutique hotel', 'Bungalow', 
'Castle', 'Condominium', 'Cottage', 'Guest suite', 'Guesthouse', 'Hotel', 'House', 'Houseboat', 'Loft', 'Other', 
'Serviced apartment', 'Townhouse', 'Villa')
* city, state, country: as reason states above.
* kinds of price
* amenities: boolean value to represents if this house provides this service. 0 is no and 1 is yes. 

## Customer Perspective
Customer need to provide his own cid (customer id) in order to login and **no password required**. Once he login, he can 
only all the listings that stored in the database.

### Customer Sign Up Page
Host need to provide basic information in order to make a new account. The information need to provided lists below:
* cid: host id. It allows host to customize his own id. But it need to be unique to distinguish other's uid. Each user
have one unique uid. **It cannot be empty.**
* canme: name of the customer. It can be empty.
* cphone: phone number. It can be empty.
* cemail: email address. It can be empty.
* dob: date of birth. **It cannot be empty** and must strictly followed the format **'YYYY-MM-DD'**.
* cpic: host picture. It can be empty and program does not check if it is a valid url.

### Rental Space (Customer/Visitor View)
He can see all the listing that stored in the database. The main page only show the information about sid, title, spic, 
bath_num, bed_num, person_capacity of a house. For more information, click `More Info`. It will show all the 
information about selected house. If no house has been selected, nothing happened. Users can also view their personal 
information by clicking `My Profile` and edit it. Clicking `My Reservation` can show all the reservation that this 
particular user made. Through `My Reservation`, user have ability to modify this own reservation. But booking_date,
cid, sid cannot be changed.

#### Single House Information Page:
Instead of seeing all information about selected house including rental space, price, amenities situation and host 
information. All information are read only. Visitor can also check availability of this house by clicking `Availability
Check` and make reservation by clicking `Reserve`.

#### Availability Check
When visitor click `Availability Check` button, it will go to a new window showing the reservation history including 
start date and end data. He can see the other reservation time, and choose a valid time to make reservation. If nothing
shows in the window, it means there is no reservation made for this house. Thus, all time are available to visitor. 
 
#### Reserve
Once visitor choose a valid time, he can click `Reserve` to actually make reservation. It requires visitor to provide
information about start date, end date, number of guest. All three fields are required and have to be valid. Program 
will check validity. It will compare all other reservation time to make sure no time period overlap and number of guest
is in range of person capacity to make sure number of guests not exceed.  

#### Data Visualization
We have four different data representation to visualize data to provide a clear way to both hosts and customers. For
details, please see our presentation about what the plot looks like. We provides four basic plot which can be presented
by clicking different buttons. It will guide users to a web-demonstrated plot.
* Neighborhood distribution: shows the number of rental spaces in the different locations(neighborhood).
* Price Distribution: shows the price distribution by the different locations(neighborhood).
* Property Type Pie Char: shows the percentage of different property type distribution.
* 3D House Brief Overview: shows the distribution of each house by daily price, person_capacity, neighborhood and 
property type.

#### Exit
The exit point of this program (same as clicking close at the upper left corner).

At other page (not main page), clicking close at the upper left corner will get back to one level of the window. 
 
## About Page
Provided the author and other information. 

## Data Source
* http://insideairbnb.com/get-the-data.html
* customer, reservation, review: make up by ourselves because it is private information we have no access to

## Load Data
To load our data, we have some methods that modify and insert the data. To re-load our data, please comment out the 
method ```read_load_data()``` to load the data. All the data are loaded into database through csv file and these file
should be please in the same path under the program. For demo, you do not have to re-load our data. It is automatically
stored in the database that in the dump sql file. 


## Built With
* tkinter - Python Interface Library
* pandas - Data Analysis Library
* plotly - plotting Library
* pymysql - Python MySQL Client

## Future Work (working on)
* Password - this program does not support password functionality for all users.
* Picture View - customer cannot see the actual picture through this program.
* Customize Searching - this program does not support any customized searching based on preferences.
* Scoring System - some attributes need to be evaluated, like is_superhost, is_verified, etc. For now, users can change
these values.
* Prevent SQL Injection - should escape the user input first (not implement yet) and prevent from other security threat.
