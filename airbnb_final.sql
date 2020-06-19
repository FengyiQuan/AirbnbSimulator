CREATE DATABASE IF NOT EXISTS airbnb_final;

USE airbnb_final;

DROP TABLE IF EXISTS property_owner;
CREATE TABLE property_owner
(
	hid INT PRIMARY KEY AUTO_INCREMENT,
    hurl VARCHAR(2083),
    hname VARCHAR(255) NOT NULL,
    hsince DATE NOT NULL,
    is_superhost TINYINT(1) DEFAULT FALSE,
    hpic VARCHAR(2083),
    total_listing INT DEFAULT 0,
    is_verified TINYINT(1) DEFAULT FALSE
);

DROP TABLE IF EXISTS room_type;
CREATE TABLE room_type
(
	rtype VARCHAR(255) PRIMARY KEY
);

DROP TABLE IF EXISTS property_type;
CREATE TABLE property_type
(
	ptype VARCHAR(255) PRIMARY KEY
);

DROP TABLE IF EXISTS amenities;
CREATE TABLE amenities
(
	aid INT PRIMARY KEY AUTO_INCREMENT,
    tv TINYINT(1),
    wifi TINYINT(1),
    free_parking TINYINT(1),
    kitchen TINYINT(1),
    air_conditioning TINYINT(1),
    hot_water TINYINT(1),
    smoke_detector TINYINT(1),
    hair_dryer TINYINT(1),
    CONSTRAINT unique_combine UNIQUE (tv, wifi, free_parking, kitchen, air_conditioning, hot_water, smoke_detector, hair_dryer)
);


DROP TABLE IF EXISTS address;
CREATE TABLE address
(
	neighborhood VARCHAR(255) PRIMARY KEY,
    city VARCHAR(255) NOT NULL,
    state VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL
);


DROP TABLE IF EXISTS price;
CREATE TABLE price
(
	pid INT PRIMARY KEY AUTO_INCREMENT,
    daily_price DECIMAL(10,2) NOT NULL,
    weekly_price DECIMAL(10,2),
    monthly_price DECIMAL(10,2),
    security_deposit DECIMAL(10,2) DEFAULT 0,
    cleaning_fee DECIMAL(10,2) DEFAULT 0,
    extra_people DECIMAL(10,2) DEFAULT 0
);


DROP TABLE IF EXISTS customer;
CREATE TABLE customer
(
	cid INT PRIMARY KEY AUTO_INCREMENT,
    cname VARCHAR(255) NOT NULL,
    cphone VARCHAR(15),
    cemail VARCHAR(255),
    dob DATE,
    cpic VARCHAR(2083)
);

DROP TABLE IF EXISTS rental_space;
CREATE TABLE rental_space
(
	sid INT PRIMARY KEY AUTO_INCREMENT,
    surl VARCHAR(2083),
    title VARCHAR(255) NOT NULL,
    rdescription TEXT,
    neighborhood_overview TEXT,
    spic VARCHAR(2083),
    bath_num INT DEFAULT 0,
    bed_num INT DEFAULT 0,
    last_update_at DATE,
    person_capacity INT,
    rate INT,
    ownerid INT NOT NULL,
    rtype VARCHAR(255),
    ptype VARCHAR(255),
    aid INT NOT NULL,
    neighborhood VARCHAR(255) NOT NULL,
    pid INT NOT NULL,
    CHECK (0 <= rate AND rate <= 100),
    CONSTRAINT rental_host_fk FOREIGN KEY(ownerid) REFERENCES property_owner(hid) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT rental_rtype_fk FOREIGN KEY(rtype) REFERENCES room_type(rtype) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT rental_ptype_fk FOREIGN KEY(ptype) REFERENCES property_type(ptype) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT rental_aid_fk FOREIGN KEY(aid) REFERENCES amenities(aid) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT rental_neighborhood_fk FOREIGN KEY(neighborhood) REFERENCES address(neighborhood) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT rental_pid_fk FOREIGN KEY(pid) REFERENCES price(pid) ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS review;
CREATE TABLE review
(
	review_id INT PRIMARY KEY,
    rcomment TEXT NOT NULL,
    cid INT NOT NULL,
    sid INT NOT NULL,
    
    CONSTRAINT review_cid_fk FOREIGN KEY(cid) REFERENCES customer(cid)  ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT review_sid_fk FOREIGN KEY(sid) REFERENCES rental_space(sid)  ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS reservation;
CREATE TABLE reservation
(
	rid INT PRIMARY KEY AUTO_INCREMENT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    num_guest INT,
    booking_date DATE NOT NULL,
    cid INT NOT NULL,
    sid INT NOT NULL,
    CHECK (booking_date <= start_date),
    CHECK (start_date < end_date),
    
    CONSTRAINT reservation_cid_fk FOREIGN KEY(cid) REFERENCES customer(cid) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT reservation_sid_fk FOREIGN KEY(sid) REFERENCES rental_space(sid) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Procedure --



drop procedure if exists read_address_by_neighborhood;
DELIMITER //
create procedure read_address_by_neighborhood(
IN nei varchar(45)
)
begin

	select * 
    from address
    where neighborhood = nei;

end// 
DELIMITER ;




drop procedure if exists read_rentalspace_by_neighborhood;
DELIMITER //
create procedure read_rentalspace_by_neighborhood(
IN nei varchar(45)
)
begin

	select * 
    from rental_space
    where neighborhood = nei;

end// 
DELIMITER ;

drop procedure if exists read_rentalspace_by_timeslot;
DELIMITER //

create procedure read_rentalspace_by_timeslot(
IN startdate date,
IN enddate date
)
begin

	select * from rental_space 
    where sid not in 
	(select sid 
    from reservation
    where start_date>= startdate and end_date<= enddate) ;

end// 
DELIMITER ;



drop procedure if exists get_amentity_by_ID;
DELIMITER //
create procedure get_amentity_by_ID(
IN ID int
)
begin
 declare amentityID int;
 
 select aid into amentityID from rental_space where sid = ID;
 
select tv,wifi,free_parking,kitchen,air_conditioning,hot_water,smoke_detector,hair_dryer from amenities where aid = amentityID;

end// 
DELIMITER ;


drop procedure if exists get_price_by_ID;
DELIMITER //
create procedure get_price_by_ID(
IN ID int
)
begin
 declare priceID int;
  select pid into priceID from rental_space where sid = ID;
 
	select daily_price,weekly_price,monthly_price,security_deposit,cleaning_fee,extra_people from price where price.pid = priceID;
end// 
DELIMITER ;


drop procedure if exists get_customerTable_by_cid;
DELIMITER //

create procedure get_customerTable_by_cid(
IN ID int
)
begin
  select * from customer where cid = ID;
 
end// 
DELIMITER ;

drop procedure if exists get_reservationTable_by_cid;
DELIMITER //

create procedure get_reservationTable_by_cid(
IN ID int
)
begin
  select * from reservation where cid = ID;
 
end// 
DELIMITER ;


drop procedure if exists get_reservationTable_by_sid;
DELIMITER //

create procedure get_reservationTable_by_sid(
IN ID int
)
begin
  select * from reservation where sid = ID;
 
end// 
DELIMITER ;

drop procedure if exists get_spaceInfo_by_sid;
DELIMITER //

create procedure get_spaceInfo_by_sid(
IN ID int
)
begin
  select sid,title,spic,bath_num,bed_num,person_capacity from rental_space where sid = ID;
 
end// 
DELIMITER ;

drop procedure if exists get_all_spaceInfo;
DELIMITER //

create procedure get_all_spaceInfo(
)
begin
  select sid,title,spic,bath_num,bed_num,person_capacity from rental_space;
 
end// 
DELIMITER ;

drop procedure if exists delete_sid;
DELIMITER //
create procedure delete_sid(
IN ID int
)
begin
delete from rental_space where sid = ID; 

end// 
DELIMITER ;


drop procedure if exists get_allInfo_by_sid;
DELIMITER //

create procedure get_allInfo_by_sid(
IN ID int
)
begin
select sid,surl,title,rdescription,neighborhood_overview,spic,bath_num,bed_num,last_update_at,person_capacity,rate,rtype,ptype,
rental_space.neighborhood,city,state,country,
daily_price,weekly_price,monthly_price,security_deposit,cleaning_fee,extra_people,
hid,hurl,hname,hsince,is_superhost,hpic,total_listing,is_verified,
tv,wifi,free_parking,kitchen,air_conditioning,hot_water,smoke_detector,hair_dryer 
from rental_space join price join property_owner join amenities join address
on sid = ID and rental_space.aid = amenities.aid and rental_space.pid = price.pid and hid = ownerid and address.neighborhood = rental_space.neighborhood;
end// 
DELIMITER ;


drop procedure if exists get_hosthouseInfo_by_hid;
DELIMITER //
create procedure get_hosthouseInfo_by_hid(
IN ID int
)
begin
select sid,title,spic,bath_num,bed_num,person_capacity from rental_space where ownerid = ID;
end// 
DELIMITER ;

drop procedure if exists get_reservation_by_rid;
DELIMITER //
create procedure get_reservation_by_rid(
IN ID int
)
begin
select * FROM reservation WHERE ID = rid;
end// 
DELIMITER ;

drop procedure if exists get_host_by_hid;
DELIMITER //
create procedure get_host_by_hid(
IN ID int
)
begin
select * FROM property_owner WHERE ID = hid;
end// 
DELIMITER ;

-- based on input, get the particular primary key (id)
drop procedure if exists get_aid;
DELIMITER //
create procedure get_aid(
IN itv tinyint,
IN iwifi tinyint,
IN ifree_parking tinyint,
IN ikitchen tinyint,
IN iair_conditioning tinyint,
IN ihot_water tinyint,
IN ismoke_detector tinyint,
IN ihair_dryer tinyint
)
begin

	select aid
    from amenities
    where tv = itv and wifi = iwifi and free_parking = ifree_parking and kitchen = ikitchen and air_conditioning = iair_conditioning and hot_water = ihot_water
    and smoke_detector = ismoke_detector and hair_dryer = ihair_dryer;

end// 
DELIMITER ;

drop procedure if exists get_pid;
DELIMITER //
create procedure get_pid(
IN idaily_price DECIMAL(10,2),
IN iweekly_price DECIMAL(10,2),
IN imonthly_price DECIMAL(10,2),
IN isecurity_deposit DECIMAL(10,2),
IN icleaning_fee DECIMAL(10,2),
IN iextra_people DECIMAL(10,2)
)
begin

	select pid
    from price
    where daily_price = idaily_price and weekly_price = iweekly_price and monthly_price = imonthly_price and security_deposit = isecurity_deposit and cleaning_fee = icleaning_fee and extra_people = iextra_people;

end// 
DELIMITER ;

drop procedure if exists get_neighbor;
DELIMITER //
create procedure get_neighbor(
IN ineighborhood VARCHAR(255),
IN icity VARCHAR(255),
IN istate VARCHAR(255),
IN icountry VARCHAR(255)
)
begin

	select neighborhood
    from address
    where neighborhood = ineighborhood and city = icity and state = istate and country = icountry;

end// 
DELIMITER ;


-- trigger --
drop procedure if exists initialize_total_listing;
delimiter //
create procedure initialize_total_listing(
in hid int
)
begin
declare tl int;
select count(hid) into tl from rental_space where ownerid = hid;

update property_owner
set total_listing = tl
where property_owner.hid = hid;

end//
delimiter ;

drop trigger if exists update_total_listing_after_insert;
 delimiter //

create trigger update_total_listing_after_insert 
after insert on rental_space
for each row
begin
call initialize_total_listing(new.ownerid);
end//
 
delimiter ;
 
drop trigger if exists update_total_listing_after_insert;
delimiter //

create trigger update_total_listing_after_insert 
after delete on rental_space
for each row
begin
call initialize_total_listing(ownerid);
end//
 
delimiter ;
