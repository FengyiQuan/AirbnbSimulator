#!/usr/bin/python3

import time
import datetime
import csv
import decimal
import pandas as pd
import plotly.express as px
from tkinter import ttk
from tkinter import *
import tkinter.messagebox as messagebox  # pop up
import pymysql


def connect_db():
    """
    connect to database
    :return: connection of the given database
    """
    host = 'localhost'
    user = "root"
    pwd = "ruqiulixia0220"
    db = 'airbnb_final'

    try:
        return pymysql.connect(host=host, user=user, password=pwd, db=db, charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
    except pymysql.err.OperationalError as e:
        print('Error: %d: %s' % (e.args[0], e.args[1]))


# read and load data into database
def amenity_convert(contains):
    li = contains.replace("{", "").replace("}", "").replace('"', "").split(",")
    return ['TV' in li, 'Wifi' in li, 'Free parking' in li, 'Kitchen' in li, 'Air conditioning' in li,
            'Hot water' in li, 'Smoke detector' in li, 'Hair dryer' in li]


def host_convert(data, is_superhost, pic, total_listing, is_verified):
    res = data

    # is_superhost
    if is_superhost == 't':
        res.append(True)
    else:
        res.append(False)
    res.append(pic)
    res.append(total_listing)
    # is_verified
    if is_verified == 't':
        res.append(True)
    else:
        res.append(False)
    return res


def price_convert(p1, p2):
    res = []
    p1.append(p2)
    for item in p1:
        if item:
            res.append(item.replace("$", "").replace(",", ""))
        else:
            res.append("Null")
    return res


def address_convert(neigh, city, state, country):
    return [neigh, city, state, country]


def price_comp(p1, p2):
    if p1 == 'Null' and p2 is None:
        return True
    elif p1 == 'Null' or p2 is None:
        return False
    else:
        return decimal.Decimal(p1) - p2 <= 0.001


def same_price(pl1, pl2):
    return price_comp(pl1[0], pl2['daily_price']) and price_comp(pl1[1], pl2['weekly_price']) and \
           price_comp(pl1[2], pl2['monthly_price']) and price_comp(pl1[3], pl2['security_deposit']) and \
           price_comp(pl1[4], pl2['cleaning_fee']) and price_comp(pl1[5], pl2['extra_people'])


def get_price_id(price, li):
    for i in li:
        if same_price(price, i):
            return i['pid']
    raise ValueError("No price id found. ")


def same_amen(a1, a2):
    return a1[0] == a2['tv'] and a1[1] == a2['wifi'] and a1[2] == a2['free_parking'] and a1[3] == a2['kitchen'] and \
           a1[4] == a2['air_conditioning'] and a1[5] == a2['hot_water'] and a1[6] == a2['smoke_detector'] and \
           a1[7] == a2['hair_dryer']


def get_amen_id(amen, li):
    for i in li:
        if same_amen(amen, i):
            return i['aid']
    raise ValueError("No amenity id found. ")


def rental_convert(item, aid, pid):
    res = [item[0], item[1], item[4].replace("'", "\\'"), item[7].replace("'", "\\'"), item[9].replace("'", "\\'"),
           item[17]]
    if item[54] == '':
        res.append(0)
    else:
        res.append(item[54])

    if item[55] == '':
        res.append(0)
    else:
        res.append(item[55])

    res.append(item[81])
    res.append(item[53])

    if item[86] == '':
        res = res + [100, item[19], item[52], item[51], aid, item[38], pid]
    else:
        res = res + [item[86], item[19], item[52], item[51], aid, item[38], pid]
    return res


def customer_convert(item):
    res = item[0:2]
    for attr in item[2:]:
        res.append(attr if attr is not None else 'Null')

    return res


def reserve_convert(item):
    res = item[0:3]
    res.append(item[3] if item[3] is not None else 'Null')
    res = res + item[4:]
    return res


def read_load_data():
    listing_file = 'Bostonlistings.csv'
    csv_file = open(listing_file, 'r')
    reader = csv.reader(csv_file)
    cnx = connect_db()
    host_data = []
    amenities = []
    prices = []
    rental_spaces = []
    property_type = []
    room_type = []
    address = []

    for item in reader:
        # ignore the first line
        if reader.line_num == 1:
            continue
        amenities.append(amenity_convert(item[58]))
        host_data.append(host_convert(item[19:23], item[28], item[30], item[32], item[36]))
        prices.append(price_convert(item[60:65], item[66]))
        property_type.append(item[51])
        room_type.append(item[52])
        address.append(address_convert(item[38], item[41], item[42], item[47]))

    csv_file.close()

    # remove all duplicates
    host_data = list(set([tuple(t) for t in host_data]))
    amenities = list(set([tuple(t) for t in amenities]))
    prices = list(set([tuple(t) for t in prices]))
    property_type = list(set(property_type))
    room_type = list(set(room_type))
    address = list(set([tuple(t) for t in address]))

    # load into database
    load_host_info(host_data, cnx)
    load_amen_info(amenities, cnx)
    load_price_info(prices, cnx)
    load_property_type(property_type, cnx)
    load_room_type(room_type, cnx)
    load_address_info(address, cnx)

    # fetch from database
    all_price_info = []
    all_ameni_info = []

    cur = cnx.cursor()
    select_price = "SELECT * FROM price"
    select_ameni = "SELECT * FROM amenities"

    cur.execute(select_price)

    for row in cur.fetchall():
        all_price_info.append(row)

    cur.execute(select_ameni)

    for row in cur.fetchall():
        all_ameni_info.append(row)
    cur.close()

    csv_file = open(listing_file, 'r')
    reader = csv.reader(csv_file)

    for item in reader:
        # ignore the first line
        if reader.line_num == 1:
            continue
        rental_spaces.append(rental_convert(item, get_amen_id(amenity_convert(item[58]), all_ameni_info),
                                            get_price_id(price_convert(item[60:65], item[66]), all_price_info)))
    csv_file.close()

    load_rental_info(rental_spaces, cnx)
    load_customer(cnx)
    load_review(cnx)
    load_reservation(cnx)

    cnx.close()


def load_price_info(data, cnx):
    cur = cnx.cursor()

    for pri in data:
        load_price_stmt = "INSERT INTO price (daily_price, weekly_price, monthly_price, security_deposit, " \
                          "cleaning_fee, extra_people) VALUES ({}, {}, {}, {}, {}, {});".format(pri[0], pri[1],
                                                                                                pri[2], pri[3],
                                                                                                pri[4], pri[5])
        try:
            cur.execute(load_price_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            print(e)
    cur.close()


def load_amen_info(data, cnx):
    cur = cnx.cursor()

    for amen in data:
        load_amen_stmt = "INSERT INTO amenities (tv, wifi, free_parking, kitchen, air_conditioning, hot_water, " \
                         "smoke_detector, hair_dryer) VALUES ({}, {}, {}, {}, {}, {}, {}, {});".format(amen[0], amen[1],
                                                                                                       amen[2], amen[3],
                                                                                                       amen[4], amen[5],
                                                                                                       amen[6], amen[7])
        try:
            cur.execute(load_amen_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            print(e)
    cur.close()


def load_host_info(data, cnx):
    cur = cnx.cursor()

    for host in data:
        load_host_stmt = "INSERT INTO property_owner VALUES ({}, '{}', " \
                         "'{}', '{}', {}, '{}', {}, {});".format(host[0], host[1], host[2], host[3], host[4], host[5],
                                                                 host[6], host[7])
        try:
            cur.execute(load_host_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            print(e)
    cur.close()


def load_room_type(data, cnx):
    cur = cnx.cursor()

    for r in data:
        load_room_stmt = "INSERT INTO room_type VALUES ('{}');".format(r)
        try:
            cur.execute(load_room_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            print(e)
    cur.close()


def load_property_type(data, cnx):
    cur = cnx.cursor()

    for p in data:
        load_property_stmt = "INSERT INTO property_type VALUES ('{}');".format(p)
        try:
            cur.execute(load_property_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            print(e)
    cur.close()


def load_address_info(data, cnx):
    cur = cnx.cursor()

    for a in data:
        load_address_stmt = "INSERT INTO address VALUES ('{}', '{}', '{}', '{}');".format(a[0], a[1], a[2], a[3])
        try:
            cur.execute(load_address_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            print(e)
    cur.close()


def load_rental_info(data, cnx):
    cur = cnx.cursor()

    for r in data:
        load_address_stmt = "INSERT INTO rental_space VALUES " \
                            "({}, '{}', '{}', '{}', '{}', '{}'" \
                            ", {}, {}, STR_TO_DATE('{}', '%Y-%m-%d'), {}, {}, {}, '{}'," \
                            " '{}', {}, '{}', {});".format(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8],
                                                           r[9], r[10], r[11], r[12], r[13], r[14], r[15], r[16])
        try:
            cur.execute(load_address_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            print(e)
    cur.close()


def load_customer(cnx):
    csv_file = open('customer.csv', 'r')
    reader = csv.reader(csv_file)
    cur = cnx.cursor()

    for item in reader:
        # ignore the first line
        if reader.line_num == 1:
            continue
        c = customer_convert(item)
        load_customer_stmt = "INSERT INTO customer VALUES " \
                             "({}, '{}', '{}', '{}', " \
                             "STR_TO_DATE('{}', '%m/%e/%y'), '{}')".format(c[0], c[1], c[2], c[3], c[4], c[5])
        try:
            cur.execute(load_customer_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            print(e)
    cur.close()
    csv_file.close()


def load_review(cnx):
    csv_file = open('review.csv', 'r')
    reader = csv.reader(csv_file)
    cur = cnx.cursor()

    for l in reader:
        # ignore the first line
        if reader.line_num == 1:
            continue
        review = l[1].replace("'", "\\'")

        load_review_stmt = "INSERT INTO review VALUES ({}, '{}', {}, {})".format(l[0], review, l[2], l[3])
        try:
            cur.execute(load_review_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            print(e)

    cur.close()
    csv_file.close()


def load_reservation(cnx):
    csv_file = open('reservation.csv', 'r')
    reader = csv.reader(csv_file)
    cur = cnx.cursor()

    for item in reader:
        # ignore the first line
        if reader.line_num == 1:
            continue
        r = reserve_convert(item)
        load_reserve_stmt = "INSERT INTO reservation VALUES " \
                            "({}, STR_TO_DATE('{}', '%m/%e/%y'), " \
                            "STR_TO_DATE('{}', '%m/%e/%y'), {}, " \
                            "STR_TO_DATE('{}', '%m/%e/%y'), {}, {})".format(r[0], r[1], r[2], r[3], r[4], r[5], r[6])

        try:
            cur.execute(load_reserve_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            print(e)

    cur.close()
    csv_file.close()


# --------------------------------  UI  --------------------------------
# constant
window_width = 800
window_height = 800
font_size = 16
font = 'Verdana'


def centralize_window(win, w=window_width, h=window_height):
    """
    Centralize the given window to set it into the middle of the screen.
    :param win: the window
    :param w: width of this window, default is window_width
    :param h: height of this window, default is window_height
    """
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    win.geometry('%dx%d+%d+%d' % (w, h, x, y))


class StartPage:
    """
    A start page that is a entry for both host and customer. It has two branches, one for host, one for customer.

    Attributes:
        window: a TK window that holds it.

    """

    def __init__(self, parent_window):
        """
        :param parent_window: the parent window which would be destroy at this point
        """
        # constant:
        button_height = 10

        parent_window.destroy()

        self.window = Tk()
        self.window.title('Welcome to Airbnb Info')
        centralize_window(self.window)

        Button(self.window, text="Host Login", font=font_size,
               command=lambda: HostPage(self.window),
               width=window_width, height=button_height).pack()

        Button(self.window, text="Customer Login", font=font_size,
               command=lambda: CustomerPage(self.window),
               width=window_width, height=button_height).pack()

        Button(text="Data Visualization", font=font_size,
               command=lambda: VisualizationPage(self.window),
               width=window_width, height=button_height).pack()

        Button(self.window, text="About", font=font_size,
               command=lambda: AboutPage(self.window),
               width=window_width, height=button_height).pack()

        Button(self.window, text='Exit', font=font_size,
               command=self.window.destroy,
               width=window_width, height=button_height).pack()

        self.window.mainloop()


class HostPage:
    """
    A host page designer for host. Allowed host to login in. In order to login in, host only need to provide their host
    id (hid). All the password is "" for convenient. (can be added in the future)
    """

    def __init__(self, parent_window):
        """
        :param parent_window: the parent window which would be destroy at this point
        """
        parent_window.destroy()

        self.window = Tk()
        self.window.title('Host login')
        centralize_window(self.window)

        Label(text='Host account (hid): ', font=font_size).pack(pady=25)

        self.hid = IntVar(value='Enter your host id here.')
        Entry(textvariable=self.hid, width=30, font=font_size, bg='Ivory', ).pack()

        Label(text='Password: ', font=font_size).pack(pady=25)

        # TODO: password functionality goes here

        self.admin_pass = Entry(self.window, width=30, font=font_size, bg='Ivory', show='*').pack()

        Button(self.window, text="Login", width=8, font=font_size,
               command=self.login).pack(pady=40)
        Button(self.window, text="Sign up", width=8, font=font_size,
               command=self.sign_up).pack(pady=40)
        Button(self.window, text="Back", width=8, font=font_size,
               command=self.back).pack(pady=40)

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def sign_up(self):
        HostSignUp(self.window)

    def login(self):
        """
        If the given hid exists, log in. Otherwise, pop up a warning.
        """
        if self.get_host_info() is not None:
            HostView(self.window, self.hid.get())
        else:
            messagebox.showinfo('Warning! ', 'uid or password is not correct! ')

    def back(self):
        """
        Back to start page.
        """
        StartPage(self.window)

    def get_host_info(self):
        """
        Fetch one tuple by given hid.
        :return: return the tuple of given hid, None if not exists.
        """
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            host_stmt = "SELECT * FROM property_owner WHERE hid = %s" % (self.hid.get())
            cur.execute(host_stmt)

            return cur.fetchone()
        except (TypeError, TclError) as e:
            messagebox.showinfo('Warning! ', 'hid must be number. \n' + str(e))
            print(e)
        finally:
            cnx.close()


class HostSignUp:
    def __init__(self, parent_window):
        # constant
        ft = ('Verdana', 20)

        parent_window.destroy()

        self.window = Tk()
        self.window.title('Host Sign Up')
        centralize_window(self.window)

        self.host_id = IntVar()
        self.host_url = StringVar()
        self.host_name = StringVar()
        self.is_superhost = BooleanVar()
        self.host_pic = StringVar()
        self.is_verified = BooleanVar()

        Label(text='*hid' + ': ', font=ft).grid(row=0, column=0)
        Label(text='hurl' + ': ', font=ft).grid(row=1, column=0)
        Label(text='hname' + ': ', font=ft).grid(row=2, column=0)
        Label(text='*is_superhost' + ': ', font=ft).grid(row=3, column=0)
        Label(text='hpic' + ': ', font=ft).grid(row=4, column=0)
        Label(text='*is_verified' + ': ', font=ft).grid(row=5, column=0)

        Entry(textvariable=self.host_id, font=ft).grid(row=0, column=1)
        Entry(textvariable=self.host_url, font=ft).grid(row=1, column=1)
        Entry(textvariable=self.host_name, font=ft).grid(row=2, column=1)
        Entry(textvariable=self.is_superhost, font=ft).grid(row=3, column=1)
        Entry(textvariable=self.host_pic, font=ft).grid(row=4, column=1)
        Entry(textvariable=self.is_verified, font=ft).grid(row=5, column=1)

        Button(text='Sign Up', width=8, font=font_size, command=self.sign).grid()

        Button(text='Back', width=8, font=font_size, command=self.back).grid()

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def sign(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            sign_stmt = "INSERT INTO property_owner VALUES ({}, '{}', " \
                        "'{}', '{}', {}, '{}', 0, {});".format(self.host_id.get(), self.host_url.get(),
                                                               self.host_name.get(),
                                                               time.strftime('%Y-%m-%d', time.localtime()),
                                                               self.is_superhost.get(), self.host_pic.get(),
                                                               self.is_verified.get())
            cur.execute(sign_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            messagebox.showinfo('Warning! ', 'Invalid Information! \n' + str(e))
            print(e)
        finally:
            cur.close()
            cnx.close()

    def back(self):
        HostPage(self.window)


class CustomerPage:
    """
    Customer page that allows customer to login in and sign up.
    """

    def __init__(self, parent_window):
        """
        :param parent_window: the parent window which would be destroy at this point
        """

        parent_window.destroy()

        self.window = Tk()
        self.window.title('Customer login')
        centralize_window(self.window)

        Label(text='Customer Account (cid): ', font=font_size).pack(pady=25)

        self.cid = IntVar(value='Enter your customer id here.')
        Entry(textvariable=self.cid, width=30, font=font_size, bg='Ivory').pack()

        Label(text='Password: ', font=font_size).pack(pady=25)
        Entry(self.window, width=30, font=font_size, bg='Ivory', show='*').pack()

        # TODO: password functionality goes here

        Button(text="Login", width=8, font=font_size, command=self.login).pack(pady=40)
        Button(text="Sign Up", width=8, font=font_size, command=self.sign_up).pack(pady=40)
        Button(text="Back", width=8, font=font_size, command=self.back).pack(pady=40)

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def sign_up(self):
        CustomerSignUp(self.window)

    def back(self):
        StartPage(self.window)

    def login(self):
        current_customer = self.get_customer_info()
        if current_customer is not None:
            CustomerView(self.window, current_customer['cid'])
            return
        else:
            messagebox.showinfo('Warning! ', 'uid or password is not correct! ')

    def get_customer_info(self):
        """
        Check whether the the user id is valid. (There is a record matching the given uid)
        :return: one tuple for that particular uid
        """
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            host_stmt = "SELECT * FROM customer WHERE cid = %s" % (self.cid.get())
            cur.execute(host_stmt)
            return cur.fetchone()
        except (TypeError, TclError) as e:
            messagebox.showinfo('Warning! ', 'uid must be number. \n' + str(e))
            print(e)
        finally:
            cur.close()
            cnx.close()


class CustomerSignUp:
    def __init__(self, parent_window):
        # constant
        ft = ('Verdana', 20)

        parent_window.destroy()

        self.window = Tk()
        self.window.title('Customer Sign Up')
        centralize_window(self.window)

        self.cid = IntVar()
        self.cname = StringVar()
        self.cphone = StringVar()
        self.cemail = StringVar()
        self.dob = StringVar(value='YYYY-MM-DD')
        self.cpic = StringVar()

        Label(text='*cid' + ': ', font=ft).grid(row=0, column=0)
        Label(text='cname' + ': ', font=ft).grid(row=1, column=0)
        Label(text='cphone' + ': ', font=ft).grid(row=2, column=0)
        Label(text='cemail' + ': ', font=ft).grid(row=3, column=0)
        Label(text='*dob' + ': ', font=ft).grid(row=4, column=0)
        Label(text='cpic' + ': ', font=ft).grid(row=5, column=0)

        Entry(textvariable=self.cid, font=ft).grid(row=0, column=1)
        Entry(textvariable=self.cname, font=ft).grid(row=1, column=1)
        Entry(textvariable=self.cphone, font=ft).grid(row=2, column=1)
        Entry(textvariable=self.cemail, font=ft).grid(row=3, column=1)
        Entry(textvariable=self.dob, font=ft).grid(row=4, column=1)
        Entry(textvariable=self.cpic, font=ft).grid(row=5, column=1)

        Button(text='Sign Up', width=8, font=font_size, command=self.sign).grid()

        Button(text='Back', width=8, font=font_size, command=self.back).grid()

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def sign(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            sign_stmt = "INSERT INTO customer VALUES ({}, '{}', " \
                        "'{}', '{}', '{}', '{}');".format(self.cid.get(), self.cname.get(), self.cphone.get(),
                                                          self.cemail.get(), self.dob.get(), self.cpic.get())
            cur.execute(sign_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            messagebox.showinfo('Warning! ', 'Invalid Information! \n' + str(e))
            print(e)
        finally:
            cur.close()
            cnx.close()

    def back(self):
        CustomerPage(self.window)


class HostView:
    """
    It allows them to modify their own listings, add new listing, delete listing.
    They can only see the listing that they holds.
    """

    def __init__(self, parent_window, hid):
        """
        :param parent_window: the parent window which would be destroy at this point
        :param hid: host id
        """
        parent_window.destroy()

        self.hid = hid

        self.window = Tk()
        self.window.title('Host Page')
        centralize_window(self.window)

        frame_top = Frame(width=window_width, height=window_height // 3 * 2)
        frame_bottom = Frame(width=window_width, height=window_height // 3)

        self.tree = ttk.Treeview(frame_top, show='headings', height=30)

        self.tree['columns'] = ('sid', 'title', 'spic', 'bath_num', 'bed_num', 'person_capacity')

        for heading in self.tree['columns']:
            self.tree.heading(heading, text=heading)

        # column type
        self.tree.column('sid', width=50, anchor='w')
        self.tree.column('title', width=300, anchor='w')
        self.tree.column('spic', width=300, anchor='center')
        self.tree.column('bath_num', width=60, anchor='center')
        self.tree.column('bed_num', width=60, anchor='center')
        self.tree.column('person_capacity', width=60, anchor='center')

        main_info = []

        db = connect_db()
        cursor = db.cursor()

        try:
            cursor.callproc('get_hosthouseInfo_by_hid', args=[self.hid])
            results = cursor.fetchall()
            for row in results:
                main_info.append(row)
        except pymysql.Error as e:
            print("Error: unable to fetch data")
            messagebox.showinfo('Warning! ', 'Fail to connect to database. ' + str(e))
        finally:
            cursor.close()
            db.close()

        for i in range(len(main_info)):  # write back data
            # TODO: picture func

            self.tree.insert('', i, values=(
                main_info[i]['sid'], main_info[i]['title'], main_info[i]['spic'], main_info[i]['bath_num'],
                main_info[i]['bed_num'], main_info[i]['person_capacity']))

        self.tree.pack()

        Button(frame_bottom, text='Add', width=8, font=font_size,
               command=self.add_new_listing).grid(row=0, column=0)

        Button(frame_bottom, text='Delete', width=8, font=font_size,
               command=self.delete_listing).grid(row=1, column=0)

        Button(frame_bottom, text='Modify', width=8, font=font_size,
               command=self.change_listing).grid(row=2, column=0)

        Button(frame_bottom, text='My Profile', width=8, font=font_size,
               command=self.profile).grid(row=0, column=1)

        Button(frame_bottom, text='Back', width=8, font=font_size,
               command=self.back).grid(row=1, column=1)

        frame_top.pack()
        frame_bottom.pack()

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def profile(self):
        HostProfile(self.window, self.hid)

    def get_select_id(self):
        cur_item = self.tree.focus()
        values = self.tree.item(cur_item)['values']
        if len(values) != 0:
            return values[0]
        else:
            return None

    def add_new_listing(self):
        AddNewListingPage(self.window, self.hid)

    def delete_listing(self):

        selected = self.get_select_id()
        if selected is not None:
            res = messagebox.askyesnocancel('Warning! ', 'Delete selected data? ')
            if res:
                cnx = connect_db()
                cur = cnx.cursor()

                try:
                    cur.callproc('delete_sid', args=[self.get_select_id()])
                    cnx.commit()
                    HostView(self.window, self.hid)  # refresh the window

                except Exception as e:
                    cnx.rollback()
                    print(e)
                finally:
                    cur.close()
                    cnx.close()

    def change_listing(self):
        selected = self.get_select_id()
        if selected is not None:
            RentalDetailCanModify(self.window, self.get_select_id(), self.hid)

    def back(self):
        StartPage(self.window)

    # 没用··················································

    # def tree_sort_column(self, tv, col, reverse):  # Treeview、列名、排列方式
    #     l = [(tv.set(k, col), k) for k in tv.get_children('')]
    #     l.sort(reverse=reverse)  # 排序方式
    #     # rearrange items in sorted positions
    #     for index, (val, k) in enumerate(l):  # 根据排序后索引移动
    #         tv.move(k, '', index)
    #     tv.heading(col, command=lambda: self.tree_sort_column(tv, col, not reverse))  # 重写标题，使之成为再点倒序的标题
    #


class HostProfile:
    def __init__(self, parent_window, hid):
        # constant
        ft = ('Verdana', 20)

        parent_window.destroy()

        self.window = Tk()
        self.window.title('Profile')
        centralize_window(self.window)
        self.hid = hid

        detail = ['hid', 'hurl', 'hname', 'hsince', '*is_superhost', 'hpic', 'total_listing', '*is_verified']

        for i in range(len(detail)):
            Label(text=detail[i] + ': ', font=ft).grid(row=i, column=0)

        host_info = self.get_host_info()

        self.host_hid = IntVar(value=host_info['hid'])
        self.host_hurl = StringVar(value=host_info['hurl'])
        self.host_hname = StringVar(value=host_info['hname'])
        self.host_hsince = StringVar(value=host_info['hsince'])
        self.host_is_superhost = StringVar(value=host_info['is_superhost'])
        self.host_hpic = StringVar(value=host_info['hpic'])
        self.host_total_listing = StringVar(value=host_info['total_listing'])
        self.host_is_verified = StringVar(value=host_info['is_verified'])

        Entry(textvariable=self.host_hid, font=ft, state='readonly').grid(row=0, column=1)
        Entry(textvariable=self.host_hurl, font=ft).grid(row=1, column=1)
        Entry(textvariable=self.host_hname, font=ft).grid(row=2, column=1)
        Entry(textvariable=self.host_hsince, font=ft, state='readonly').grid(row=3, column=1)
        Entry(textvariable=self.host_is_superhost, font=ft).grid(row=4, column=1)
        Entry(textvariable=self.host_hpic, font=ft).grid(row=5, column=1)
        Entry(textvariable=self.host_total_listing, font=ft, state='readonly').grid(row=6, column=1)
        Entry(textvariable=self.host_is_verified, font=ft).grid(row=7, column=1)

        Button(text='Update', width=8, font=font_size, command=self.update).grid()

        Button(text='Back', width=8, font=font_size, command=self.back).grid()

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def update(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            update_stmt = "UPDATE property_owner SET hurl = '{}', " \
                          "hname = '{}', is_superhost = '{}', hpic = '{}', " \
                          "is_verified = '{}' WHERE hid = {};".format(self.host_hurl.get(), self.host_hname.get(),
                                                                      self.host_is_superhost.get(),
                                                                      self.host_hpic.get(), self.host_is_verified.get(),
                                                                      self.hid)
            cur.execute(update_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def get_host_info(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            cur.callproc('get_host_by_hid', args=[self.hid])
            return cur.fetchone()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def back(self):
        HostView(self.window, self.hid)


class RentalDetailCanModify:

    def __init__(self, parent_window, sid, hid):
        # constant
        ft = 10

        parent_window.destroy()

        self.window = Tk()
        self.window.title('Detail')
        centralize_window(self.window)

        self.sid = sid
        self.hid = hid

        info = self.get_all_info()

        self.sid = StringVar(value=info['sid'])
        self.surl = StringVar(value=info['surl'])
        self.title = StringVar(value=info['title'])
        self.descript = StringVar(value=info['rdescription'])
        self.nvw = StringVar(value=info['neighborhood_overview'])
        self.pc = StringVar(value=info['spic'])
        self.bath_num = IntVar(value=info['bath_num'])
        self.bed_num = IntVar(value=info['bed_num'])
        self.per_cap = IntVar(value=info['person_capacity'])
        self.rate = IntVar(value=info['rate'])
        self.neighb = StringVar(value=info['neighborhood'])
        self.city = StringVar(value=info['city'])
        self.state = StringVar(value=info['state'])
        self.country = StringVar(value=info['country'])
        self.dpr = DoubleVar(value=info['daily_price'])
        self.wpr = DoubleVar(value=info['weekly_price'])
        self.mpr = DoubleVar(value=info['monthly_price'])
        self.sdep = DoubleVar(value=info['security_deposit'])
        self.cfe = DoubleVar(value=info['cleaning_fee'])
        self.exp = DoubleVar(value=info['extra_people'])
        self.tv = BooleanVar(value=info['tv'])
        self.wifi = BooleanVar(value=info['wifi'])
        self.fre_p = BooleanVar(value=info['free_parking'])
        self.kitche = BooleanVar(value=info['kitchen'])
        self.ac = BooleanVar(value=info['air_conditioning'])
        self.hwa = BooleanVar(value=info['hot_water'])
        self.sde = BooleanVar(value=info['smoke_detector'])
        self.hdy = BooleanVar(value=info['hair_dryer'])

        rtype_list = ['Entire home/apt', 'Hotel room', 'Private room', 'Shared room']

        self.combox_rtype = ttk.Combobox(textvariable=StringVar(), state='readonly', values=rtype_list)
        self.combox_rtype.current(rtype_list.index(info['rtype']))

        ptype_list = ['Apartment', 'Barn', 'Bed and breakfast', 'Boat', 'Boutique hotel', 'Bungalow', 'Castle',
                      'Condominium', 'Cottage', 'Guest suite', 'Guesthouse', 'Hotel', 'House', 'Houseboat', 'Loft',
                      'Other', 'Serviced apartment', 'Townhouse', 'Villa']
        self.combox_ptype = ttk.Combobox(textvariable=StringVar(), state='readonly', values=ptype_list)
        self.combox_ptype.current(ptype_list.index(info['ptype']))

        component = {'*sid': Entry(textvariable=self.sid, font=ft, state='readonly'),
                     'surl': Entry(textvariable=self.surl, font=ft),
                     'title': Entry(textvariable=self.title, font=ft),
                     'rdescription': Entry(textvariable=self.descript, font=ft),
                     'neighborhood_overview': Entry(textvariable=self.nvw, font=ft),
                     'spic': Entry(textvariable=self.pc, font=ft),
                     '*bath_num': Entry(textvariable=self.bath_num, font=ft),
                     '*bed_num': Entry(textvariable=self.bed_num, font=ft),
                     '*person_capacity': Entry(textvariable=self.per_cap, font=ft),
                     '*rate': Entry(textvariable=self.rate, font=ft),
                     '*rtype': self.combox_rtype, '*ptype': self.combox_ptype,
                     'neighborhood': Entry(textvariable=self.neighb, font=ft),
                     '*city': Entry(textvariable=self.city, font=ft, state='readonly'),
                     '*state': Entry(textvariable=self.state, font=ft, state='readonly'),
                     '*country': Entry(textvariable=self.country, font=ft, state='readonly'),
                     '*daily_price': Entry(textvariable=self.dpr, font=ft),
                     '*weekly_price': Entry(textvariable=self.wpr, font=ft),
                     '*monthly_price': Entry(textvariable=self.mpr, font=ft),
                     '*security_deposit': Entry(textvariable=self.sdep, font=ft),
                     '*cleaning_fee': Entry(textvariable=self.cfe, font=ft),
                     '*extra_people': Entry(textvariable=self.exp, font=ft),
                     '*tv': Entry(textvariable=self.tv, font=ft), '*wifi': Entry(textvariable=self.wifi, font=ft),
                     '*free_parking': Entry(textvariable=self.fre_p, font=ft),
                     '*kitchen': Entry(textvariable=self.kitche, font=ft),
                     '*air_conditioning': Entry(textvariable=self.ac, font=ft),
                     '*hot_water': Entry(textvariable=self.hwa, font=ft),
                     '*smoke_detector': Entry(textvariable=self.sde, font=ft),
                     '*hair_dryer': Entry(textvariable=self.hdy, font=ft)}

        row = 0
        col = 0
        for key in component:
            if row > 14:
                row = 0
                col = 2
            prev_col = col
            Label(text=key + ': ', font=10).grid(row=row, column=col)
            col += 1
            component[key].grid(row=row, column=col)
            row += 1
            col = prev_col

        Button(text='Update', width=8, font=font_size, command=self.add_new_listing).grid()
        Button(text='Back', width=8, font=font_size, command=self.back).grid()

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def get_amenities_id(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            cur.callproc('get_aid',
                         args=[self.tv.get(), self.wifi.get(), self.fre_p.get(), self.kitche.get(), self.ac.get(),
                               self.hwa.get(), self.sde.get(), self.hdy.get()])
            res = cur.fetchone()
            if res is None:
                self.add_new_amenities(cnx)
                return self.get_amenities_id()
            else:
                return res
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def add_new_amenities(self, cnx):
        cur = cnx.cursor()
        try:
            add_stmt = "INSERT amenities(tv, wifi, free_parking, kitchen, " \
                       "air_conditioning, hot_water, smoke_detector, hair_dryer) VALUES" \
                       "({}, {}, {}, {}, {}, " \
                       "{}, {}, {})".format(self.tv.get(), self.wifi.get(), self.fre_p.get(), self.kitche.get(),
                                            self.ac.get(), self.hwa.get(), self.sde.get(), self.hdy.get())
            cur.execute(add_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()

    def get_price_id(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            cur.callproc('get_pid',
                         args=[self.dpr.get(), self.wpr.get(), self.mpr.get(), self.sdep.get(), self.cfe.get(),
                               self.exp.get()])
            res = cur.fetchone()
            if res is None:
                self.add_new_price(cnx)
                return self.get_price_id()
            else:
                return res
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def add_new_price(self, cnx):
        cur = cnx.cursor()
        try:
            add_stmt = "INSERT price(daily_price, weekly_price, monthly_price, security_deposit, " \
                       "cleaning_fee, extra_people) VALUES ({}, {}, {}, {}, {}, " \
                       "{})".format(self.dpr.get(), self.wpr.get(), self.mpr.get(), self.sdep.get(), self.cfe.get(),
                                    self.exp.get())
            cur.execute(add_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()

    def get_address_neigh(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            cur.callproc('get_neighbor',
                         args=[self.neighb.get(), self.city.get(), self.state.get(), self.country.get()])
            res = cur.fetchone()
            if res is None:
                self.add_new_address(cnx)
                return self.get_address_neigh()
            else:
                return res
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def add_new_address(self, cnx):
        cur = cnx.cursor()
        try:
            add_stmt = "INSERT address VALUES ('{}', '{}', '{}', " \
                       "'{}')".format(self.neighb.get(), self.city.get(), self.state.get(), self.country.get())
            cur.execute(add_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()

    # ability to change data in the database
    def add_new_listing(self):
        address_neigh = self.get_address_neigh()['neighborhood']
        price_id = self.get_price_id()['pid']
        amen_id = self.get_amenities_id()['aid']
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            update_stmt = "UPDATE rental_space SET " \
                          "surl = '{}', title = '{}', rdescription = '{}', neighborhood_overview = '{}', " \
                          "spic = '{}', bath_num = {}, bed_num = {}, last_update_at = '{}', person_capacity = {}, " \
                          "rate = {}, rtype = '{}', ptype = '{}', aid = {}, neighborhood = '{}', pid = {} " \
                          "WHERE sid = {};".format(self.surl.get(), self.title.get(), self.descript.get(),
                                                   self.nvw.get(), self.pc.get(), self.bath_num.get(),
                                                   self.bed_num.get(), time.strftime('%Y-%m-%d', time.localtime()),
                                                   self.per_cap.get(), self.rate.get(), self.combox_rtype.get(),
                                                   self.combox_ptype.get(), amen_id, address_neigh, price_id,
                                                   self.sid.get())

            cur.execute(update_stmt)
            cnx.commit()

        except Exception as e:
            messagebox.showinfo('Warning', 'Invalid information! \n' + str(e))
            cnx.rollback()
            print(e)

        finally:
            cur.close()
            cnx.close()

    def back(self):
        HostView(self.window, self.hid)

    def get_all_info(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            cur.callproc('get_allInfo_by_sid', args=[self.sid])
            return cur.fetchone()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()


class AddNewListingPage:
    def __init__(self, parent_window, host_id):
        ft = 10
        parent_window.destroy()

        self.hid = host_id

        self.window = Tk()
        self.window.title('Add New Info Page')
        centralize_window(self.window)

        self.surl = StringVar()
        self.title = StringVar()
        self.descript = StringVar()
        self.nvw = StringVar()
        self.pc = StringVar()
        self.bath_num = IntVar()
        self.bed_num = IntVar()
        self.per_cap = IntVar()
        self.rate = IntVar()
        self.neighb = StringVar()
        self.city = StringVar(value='Boston')
        self.state = StringVar(value='MA')
        self.country = StringVar(value='United States')
        self.dpr = DoubleVar()
        self.wpr = DoubleVar()
        self.mpr = DoubleVar()
        self.sdep = DoubleVar()
        self.cfe = DoubleVar()
        self.exp = DoubleVar()
        self.tv = BooleanVar()
        self.wifi = BooleanVar()
        self.fre_p = BooleanVar()
        self.kitche = BooleanVar()
        self.ac = BooleanVar()
        self.hwa = BooleanVar()
        self.sde = BooleanVar()
        self.hdy = BooleanVar()

        self.combox_rtype = ttk.Combobox(textvariable=StringVar(), state='readonly')
        self.combox_rtype['values'] = ('Entire home/apt', 'Hotel room', 'Private room', 'Shared room')
        self.combox_ptype = ttk.Combobox(textvariable=StringVar(), state='readonly')
        self.combox_ptype['values'] = (
            'Apartment', 'Barn', 'Bed and breakfast', 'Boat', 'Boutique hotel', 'Bungalow', 'Castle', 'Condominium',
            'Cottage', 'Guest suite', 'Guesthouse', 'Hotel', 'House', 'Houseboat', 'Loft', 'Other',
            'Serviced apartment', 'Townhouse', 'Villa')

        component = {'surl': Entry(textvariable=self.surl, font=ft),
                     'title': Entry(textvariable=self.title, font=ft),
                     'rdescription': Entry(textvariable=self.descript, font=ft),
                     'neighborhood_overview': Entry(textvariable=self.nvw, font=ft),
                     'spic': Entry(textvariable=self.pc, font=ft),
                     '*bath_num': Entry(textvariable=self.bath_num, font=ft),
                     '*bed_num': Entry(textvariable=self.bed_num, font=ft),
                     '*person_capacity': Entry(textvariable=self.per_cap, font=ft),
                     '*rate': Entry(textvariable=self.rate, font=ft),
                     '*rtype': self.combox_rtype, '*ptype': self.combox_ptype,
                     'neighborhood': Entry(textvariable=self.neighb, font=ft),
                     '*city': Entry(textvariable=self.city, font=ft, state='readonly'),
                     '*state': Entry(textvariable=self.state, font=ft, state='readonly'),
                     '*country': Entry(textvariable=self.country, font=ft, state='readonly'),
                     '*daily_price': Entry(textvariable=self.dpr, font=ft),
                     '*weekly_price': Entry(textvariable=self.wpr, font=ft),
                     '*monthly_price': Entry(textvariable=self.mpr, font=ft),
                     '*security_deposit': Entry(textvariable=self.sdep, font=ft),
                     '*cleaning_fee': Entry(textvariable=self.cfe, font=ft),
                     '*extra_people': Entry(textvariable=self.exp, font=ft),
                     '*tv': Entry(textvariable=self.tv, font=ft), 'wifi': Entry(textvariable=self.wifi, font=ft),
                     '*free_parking': Entry(textvariable=self.fre_p, font=ft),
                     '*kitchen': Entry(textvariable=self.kitche, font=ft),
                     '*air_conditioning': Entry(textvariable=self.ac, font=ft),
                     '*hot_water': Entry(textvariable=self.hwa, font=ft),
                     '*smoke_detector': Entry(textvariable=self.sde, font=ft),
                     '*hair_dryer': Entry(textvariable=self.hdy, font=ft)}

        row = 0
        col = 0
        for key in component:
            if row > 14:
                row = 0
                col = 2
            prev_col = col
            Label(text=key + ': ', font=10).grid(row=row, column=col)
            col += 1
            component[key].grid(row=row, column=col)
            row += 1
            col = prev_col

        Button(text='Add', width=8, font=font_size, command=self.add_new_listing).grid()
        Button(text='Back', width=8, font=font_size, command=self.back).grid()

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def get_amenities_id(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            cur.callproc('get_aid',
                         args=[self.tv.get(), self.wifi.get(), self.fre_p.get(), self.kitche.get(), self.ac.get(),
                               self.hwa.get(), self.sde.get(), self.hdy.get()])
            res = cur.fetchone()
            if res is None:
                self.add_new_amenities(cnx)
                return self.get_amenities_id()
            else:
                return res
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def add_new_amenities(self, cnx):
        cur = cnx.cursor()
        try:
            add_stmt = "INSERT amenities(tv, wifi, free_parking, kitchen, " \
                       "air_conditioning, hot_water, smoke_detector, hair_dryer) VALUES" \
                       "({}, {}, {}, {}, {}, " \
                       "{}, {}, {})".format(self.tv.get(), self.wifi.get(), self.fre_p.get(), self.kitche.get(),
                                            self.ac.get(), self.hwa.get(), self.sde.get(), self.hdy.get())
            cur.execute(add_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def get_price_id(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            cur.callproc('get_pid',
                         args=[self.dpr.get(), self.wpr.get(), self.mpr.get(), self.sdep.get(), self.cfe.get(),
                               self.exp.get()])
            res = cur.fetchone()
            if res is None:
                self.add_new_price(cnx)
                return self.get_price_id()
            else:
                return res
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def add_new_price(self, cnx):
        cur = cnx.cursor()
        try:
            add_stmt = "INSERT price(daily_price, weekly_price, monthly_price, security_deposit, " \
                       "cleaning_fee, extra_people) VALUES ({}, {}, {}, {}, {}, " \
                       "{})".format(self.dpr.get(), self.wpr.get(), self.mpr.get(), self.sdep.get(), self.cfe.get(),
                                    self.exp.get())
            cur.execute(add_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()

    def get_address_neigh(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            cur.callproc('get_neighbor',
                         args=[self.neighb.get(), self.city.get(), self.state.get(), self.country.get()])
            res = cur.fetchone()
            if res is None:
                self.add_new_address(cnx)
                return self.get_address_neigh()
            else:
                return res
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def add_new_address(self, cnx):
        cur = cnx.cursor()
        try:
            add_stmt = "INSERT address VALUES ('{}', '{}', '{}', " \
                       "'{}')".format(self.neighb.get(), self.city.get(), self.state.get(), self.country.get())
            cur.execute(add_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()

    # ability to change data in the database
    def add_new_listing(self):
        host_id = self.hid
        address_neigh = self.get_address_neigh()['neighborhood']
        price_id = self.get_price_id()['pid']
        amen_id = self.get_amenities_id()['aid']
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            insert = "INSERT INTO rental_space(surl, title, rdescription, neighborhood_overview, spic, bath_num, " \
                     "bed_num, last_update_at, person_capacity, rate, ownerid, rtype, ptype, aid, neighborhood, pid)" \
                     " VALUES ('{}', '{}', '{}', '{}', '{}', {}, {}, '{}', {}, {}, {}, '{}', '{}', {}, '{}', " \
                     "{});".format(self.surl.get(), self.title.get(), self.descript.get(),
                                   self.nvw.get(), self.pc.get(), self.bath_num.get(),
                                   self.bed_num.get(), time.strftime('%Y-%m-%d', time.localtime()), self.per_cap.get(),
                                   self.rate.get(), host_id, self.combox_rtype.get(), self.combox_ptype.get(), amen_id,
                                   address_neigh, price_id)
            cur.execute(insert)
            cnx.commit()
        except Exception as e:
            messagebox.showinfo('Warning', 'Invalid information! \n' + str(e))
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def back(self):
        HostView(self.window, self.hid)


class CustomerView:
    def __init__(self, parent_window, customer_id):
        parent_window.destroy()

        self.window = Tk()
        self.window.title('Customer Page')
        centralize_window(self.window)

        self.cid = customer_id

        self.tree = ttk.Treeview(show='headings', height=30)

        self.tree['columns'] = ('sid', 'title', 'spic', 'bath_num', 'bed_num', 'person_capacity')

        for heading in self.tree['columns']:
            self.tree.heading(heading, text=heading)

        # heading configuration
        self.tree.column('sid', width=50, anchor='w')
        self.tree.column('title', width=300, anchor='w')
        self.tree.column('spic', width=300, anchor='center')
        self.tree.column('bath_num', width=60, anchor='center')
        self.tree.column('bed_num', width=60, anchor='center')
        self.tree.column('person_capacity', width=100, anchor='center')

        main_info = self.get_all_space_info()

        for i in range(len(main_info)):  # write back data
            # TODO: picture func
            self.tree.insert('', i, values=(
                main_info[i]['sid'], main_info[i]['title'], main_info[i]['spic'], main_info[i]['bath_num'],
                main_info[i]['bed_num'], main_info[i]['person_capacity']))

        self.tree.pack()

        Button(text='More Info', width=15, font=font_size, command=self.show_info_listing).pack(
            pady=10)

        Button(text='My Profile', width=15, font=font_size, command=self.show_profile_info).pack(
            pady=10)

        Button(text='My Reservation', width=15, font=font_size, command=self.show_reserve_info).pack(
            pady=10)

        Button(text='Back', width=15, font=font_size, command=self.back).pack(pady=10)

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    @staticmethod
    def get_all_space_info():
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            cur.callproc('get_all_spaceInfo')
            return cur.fetchall()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def show_reserve_info(self):
        """
        show the user's reservation
        """
        ReservationInfo(self.window, self.cid)

    def get_select_id(self):
        cur_item = self.tree.focus()
        values = self.tree.item(cur_item)['values']
        if len(values) != 0:
            return values[0]
        else:
            return None

    def show_info_listing(self):
        selected = self.get_select_id()
        if selected is not None:
            RentalDetailReadOnly(self.window, selected, self.cid)

    def show_profile_info(self):
        CustomerProfile(self.window, self.cid)

    def back(self):
        StartPage(self.window)


class CustomerProfile:
    def __init__(self, parent_window, customer_id):
        # constant
        ft = ('Verdana', 20)

        parent_window.destroy()

        self.window = Tk()
        self.window.title('Profile')
        centralize_window(self.window)
        self.cid = customer_id

        detail = ['*cid', 'cname', 'cphone', 'cemail', '*dob', 'cpic']

        for i in range(len(detail)):
            Label(text=detail[i] + ': ', font=ft).grid(row=i, column=0)

        cus_info = self.get_cus_info()

        self.cus_cid = IntVar(value=cus_info['cid'])
        self.cus_cname = StringVar(value=cus_info['cname'])
        self.cus_phone = StringVar(value=cus_info['cphone'])
        self.cus_email = StringVar(value=cus_info['cemail'])
        self.cus_dob = StringVar(value=cus_info['dob'])
        self.cus_pic = StringVar(value=cus_info['cpic'])

        Entry(textvariable=self.cus_cid, font=ft, state='readonly').grid(row=0, column=1)
        Entry(textvariable=self.cus_cname, font=ft).grid(row=1, column=1)
        Entry(textvariable=self.cus_phone, font=ft).grid(row=2, column=1)
        Entry(textvariable=self.cus_email, font=ft).grid(row=3, column=1)
        Entry(textvariable=self.cus_dob, font=ft).grid(row=4, column=1)
        Entry(textvariable=self.cus_pic, font=ft).grid(row=5, column=1)

        Button(text='Update', width=8, font=font_size, command=self.update).grid()

        Button(text='Back', width=8, font=font_size, command=self.back).grid()

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def update(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            update_stmt = "UPDATE customer SET cname = '{}', cphone = '{}', " \
                          "cemail = '{}', dob = '{}', cpic = '{}' WHERE cid = {};".format(self.cus_cname.get(),
                                                                                          self.cus_phone.get(),
                                                                                          self.cus_email.get(),
                                                                                          self.cus_dob.get(),
                                                                                          self.cus_pic.get(),
                                                                                          self.cid)
            cur.execute(update_stmt)
            cnx.commit()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def get_cus_info(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            cur.callproc('get_customerTable_by_cid', args=[self.cid])
            return cur.fetchone()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def back(self):
        CustomerView(self.window, self.cid)


class ReservationInfo:
    def __init__(self, parent_window, cid):
        parent_window.destroy()

        self.window = Tk()
        self.window.title('Your Reservation')
        centralize_window(self.window)
        self.cid = cid

        self.tree = ttk.Treeview(show='headings', height=30)

        self.tree['columns'] = ('rid', 'start_date', 'end_date', 'num_guest', 'booking_date', 'cid', 'sid')

        for heading in self.tree['columns']:
            self.tree.heading(heading, text=heading)

        # heading configuration
        self.tree.column('rid', width=50, anchor='center')
        self.tree.column('start_date', width=100, anchor='center')
        self.tree.column('end_date', width=100, anchor='center')
        self.tree.column('num_guest', width=100, anchor='center')
        self.tree.column('booking_date', width=100, anchor='center')
        self.tree.column('cid', width=50, anchor='center')
        self.tree.column('sid', width=50, anchor='center')

        main_info = self.get_user_reserv()

        for i in range(len(main_info)):  # write back data
            self.tree.insert('', i, values=(
                main_info[i]['rid'], main_info[i]['start_date'], main_info[i]['end_date'], main_info[i]['num_guest'],
                main_info[i]['booking_date'], main_info[i]['cid'], main_info[i]['sid']))

        self.tree.pack()

        Button(text='Modify', width=20, font=font_size, command=self.modify).pack()
        Button(text='Back', width=20, font=font_size, command=self.back).pack()

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def get_user_reserv(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            cur.callproc('get_reservationTable_by_cid', args=[self.cid])
            return cur.fetchall()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def get_select_id(self):
        cur_item = self.tree.focus()
        values = self.tree.item(cur_item)['values']
        if len(values) != 0:
            return values[0]
        else:
            return None

    def modify(self):
        selected = self.get_select_id()
        if selected is not None:
            ReservationModify(self.window, selected)

    def back(self):
        CustomerView(self.window, self.cid)


class ReservationModify:
    def __init__(self, parent_window, rid):
        ft = ('Verdana', 20)

        parent_window.destroy()

        self.window = Tk()
        self.window.title('Detail')
        centralize_window(self.window)
        self.rid = rid

        detail = ['*start_date', '*end_date', '*num_guest', '*booking_date', '*cid', '*sid']

        for i in range(len(detail)):
            Label(text=detail[i] + ': ', font=ft).grid(row=i, column=0)

        reserve_info = self.get_detail()
        self.start_date = StringVar(value=reserve_info['start_date'])
        self.end_date = StringVar(value=reserve_info['end_date'])
        self.num_guest = IntVar(value=reserve_info['num_guest'])
        self.booking_date = StringVar(value=reserve_info['booking_date'])
        self.cid = IntVar(value=reserve_info['cid'])
        self.sid = IntVar(value=reserve_info['sid'])

        Entry(textvariable=self.start_date, font=ft).grid(row=0, column=1)
        Entry(textvariable=self.end_date, font=ft).grid(row=1, column=1)
        Entry(textvariable=self.num_guest, font=ft).grid(row=2, column=1)
        Entry(textvariable=self.booking_date, font=ft, state='readonly').grid(row=3, column=1)
        Entry(textvariable=self.cid, font=ft, state='readonly').grid(row=4, column=1)
        Entry(textvariable=self.sid, font=ft, state='readonly').grid(row=5, column=1)

        Button(text='Update', width=8, font=font_size, command=self.modify).grid()

        Button(text='Back', width=8, font=font_size, command=self.back).grid()

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def get_other_reserve(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            cur.callproc('get_reservationTable_by_sid', args=[self.sid.get()])
            return cur.fetchall()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def check_ava(self):
        other_reserve = self.get_other_reserve()
        start = self.start_date.get()
        end = self.end_date.get()
        person_cap = self.get_person_capacity()
        result = True and self.num_guest.get() <= person_cap
        for reserve in other_reserve:
            if reserve['rid'] == self.rid:
                break
            start_date = datetime.datetime.strftime(reserve['start_date'], '%Y-%m-%d')
            end_date = datetime.datetime.strftime(reserve['end_date'], '%Y-%m-%d')

            result = result and not (start_date < end and end_date > start)
        return result

    def get_person_capacity(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            cur.callproc('get_spaceInfo_by_sid', args=[self.sid.get()])
            return cur.fetchone()['person_capacity']
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def get_detail(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            cur.callproc('get_reservation_by_rid', args=[self.rid])
            return cur.fetchone()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def modify(self):
        cnx = connect_db()
        cur = cnx.cursor()
        if self.check_ava():
            try:
                change_stmt = "UPDATE reservation SET start_date = '{}', " \
                              "end_date = '{}', num_guest = {}, booking_date = '{}', " \
                              "cid = {}, sid = {} WHERE rid = {}".format(self.start_date.get(), self.end_date.get(),
                                                                         self.num_guest.get(), self.booking_date.get(),
                                                                         self.cid.get(), self.sid.get(), self.rid)
                cur.execute(change_stmt)
                cnx.commit()
            except Exception as e:
                cnx.rollback()
                messagebox.showinfo('Warning! ', 'Information may not valid! \n' + str(e))
                print(e)
            finally:
                cur.close()
                cnx.close()
        else:
            messagebox.showinfo('Warning! ', 'Time is not available or number of guests exceed! ')

    def get_cid(self):
        return self.get_detail()['cid']

    def back(self):
        ReservationInfo(self.window, self.get_cid())


class RentalDetailReadOnly:

    def __init__(self, parent_window, sid, customer_id):
        ft = ('Verdana', 20)

        parent_window.destroy()

        self.window = Tk()
        self.window.title('Detail')
        centralize_window(self.window)

        self.cid = customer_id
        self.sid = sid

        detail = self.get_detail()

        row = 0
        col = 0
        for key in detail:
            if row > 19:
                row = 0
                col = 2
            prev_col = col
            Label(text=key + ': ', font=ft).grid(row=row, column=col)
            col += 1
            Entry(textvariable=StringVar(value=detail[key]), font=ft, state='readonly').grid(row=row, column=col)
            row += 1
            col = prev_col

        Button(text='Availability Check', width=20, font=font_size,
               command=self.availability_check).grid(row=20, column=0, pady=25)
        Button(text='Reserve', width=20, font=font_size,
               command=self.reserve).grid(row=20, column=1, pady=25)
        Button(text='Back', width=20, font=font_size,
               command=self.back).grid(row=20, column=2, pady=25)

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def get_detail(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            cur.callproc('get_allInfo_by_sid', args=[self.sid])
            return cur.fetchone()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def availability_check(self):
        ReservationCheckPage(self.window, self.cid, self.sid)

    def reserve(self):
        ReservePage(self.window, self.sid, self.cid)

    def back(self):
        CustomerView(self.window, self.cid)


class ReservationCheckPage:
    def __init__(self, parent_window, cid, sid):
        parent_window.destroy()

        self.window = Tk()
        self.window.title('Reservation History')
        centralize_window(self.window)
        self.cid = cid
        self.sid = sid

        self.tree = ttk.Treeview(show='headings', height=30)

        self.tree['columns'] = ('start_date', 'end_date')

        for heading in self.tree['columns']:
            self.tree.heading(heading, text=heading)

        # heading configuration
        self.tree.column('start_date', width=100)
        self.tree.column('end_date', width=100)

        main_info = self.get_user_reserv()

        for i in range(len(main_info)):  # write back data
            self.tree.insert('', i, values=(main_info[i]['start_date'], main_info[i]['end_date']))

        self.tree.pack()

        Button(text='Back', width=20, font=font_size, command=self.back).pack()

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def get_user_reserv(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            cur.callproc('get_reservationTable_by_sid', args=[self.sid])
            return cur.fetchall()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def back(self):
        RentalDetailReadOnly(self.window, self.sid, self.cid)


class ReservePage:
    def __init__(self, parent_window, sid, cid):
        ft = ('Verdana', 20)

        parent_window.destroy()

        self.window = Tk()
        self.window.title('Make Reservation!!')
        centralize_window(self.window)

        self.cid = cid
        self.sid = sid

        self.start = StringVar(value='YYYY-MM-DD')
        self.end = StringVar(value='YYYY-MM-DD')
        self.num_guest = IntVar()

        Label(text='*Start Date : ', font=ft).grid(row=0, column=0)
        Entry(textvariable=self.start, font=ft).grid(row=0, column=1)
        Label(text='*End Date : ', font=ft).grid(row=1, column=0)
        Entry(textvariable=self.end, font=ft).grid(row=1, column=1)
        Label(text='*Number of guest : ', font=ft).grid(row=2, column=0)
        Entry(textvariable=self.num_guest, font=ft).grid(row=2, column=1)

        Button(text='Reserve', width=20, font=font_size, command=self.make_reservation).grid(row=3, column=0)
        Button(text='Back', width=20, font=font_size, command=self.back).grid(row=4, column=0)

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def make_reservation(self):
        if self.check_ava():
            cnx = connect_db()
            cur = cnx.cursor()
            make_stmt = "INSERT reservation(start_date, end_date, num_guest, booking_date, cid, sid)" \
                        " VALUES('{}', '{}', {}, '{}', {}, {})".format(self.start.get(), self.end.get(),
                                                                       self.num_guest.get(),
                                                                       time.strftime('%Y-%m-%d', time.localtime()),
                                                                       self.cid,
                                                                       self.sid)
            try:
                cur.execute(make_stmt)
                cnx.commit()
            except Exception as e:
                cnx.rollback()
                messagebox.showinfo('Warning! ', 'Information may not valid! \n' + str(e))
                print(e)
            finally:
                cur.close()
                cnx.close()
        else:
            messagebox.showinfo('Warning! ', 'Time is not available or number of guests exceed! ')

    def check_ava(self):
        other_reserve = self.get_other_reserve()
        start = self.start.get()
        end = self.end.get()
        person_cap = self.get_person_capacity()
        result = True and self.num_guest.get() <= person_cap
        for reserve in other_reserve:
            start_date = datetime.datetime.strftime(reserve['start_date'], '%Y-%m-%d')
            end_date = datetime.datetime.strftime(reserve['end_date'], '%Y-%m-%d')

            result = result and not (start_date < end and end_date > start)
        return result

    def get_person_capacity(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            cur.callproc('get_spaceInfo_by_sid', args=[self.sid])
            return cur.fetchone()['person_capacity']
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def get_other_reserve(self):
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            cur.callproc('get_reservationTable_by_sid', args=[self.sid])
            return cur.fetchall()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    def back(self):
        RentalDetailReadOnly(self.window, self.sid, self.cid)


class VisualizationPage:
    def __init__(self, parent_window):
        # constant:
        button_height = 10

        parent_window.destroy()

        self.window = Tk()
        self.window.title('Data Visualization')
        centralize_window(self.window)

        Button(self.window, text="Neighborhood Distribution", font=font_size,
               command=self.neighborhood_distribution_view,
               width=window_width, height=button_height).pack()

        Button(self.window, text="Price Distribution", font=font_size,
               command=self.price_distribution_view,
               width=window_width, height=button_height).pack()

        Button(text="Property Type Pie Char", font=font_size,
               command=self.pie_chart_ptype,
               width=window_width, height=button_height).pack()

        Button(self.window, text="3D House Brief Overview", font=font_size,
               command=self.threed_bubble_chart_house_brief_overview,
               width=window_width, height=button_height).pack()

        Button(self.window, text='Back', font=font_size,
               command=self.back,
               width=window_width, height=button_height).pack()

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def back(self):
        StartPage(self.window)

    @staticmethod
    def neighborhood_distribution_view():
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            stm = "select * from rental_space"
            cur.execute(stm)
            df = pd.DataFrame(cur.fetchall())
            nei_col = ["number of listings", "neighborhood"]
            nei = df[nei_col]
            neighbourhood_count = nei.groupby("neighborhood").agg("count").reset_index(inplace=False)
            fig = px.bar(neighbourhood_count, x="neighborhood", y="sid", color="sid")
            fig.show()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    @staticmethod
    def price_distribution_view():
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            stm = "select sid, neighborhood, rtype, daily_price from rental_space, price " \
                  "where rental_space.pid = price.pid"
            cur.execute(stm)
            df = pd.DataFrame(cur.fetchall())
            graph2 = px.scatter(df, x="daily_price", y="neighborhood")
            graph2.show()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    @staticmethod
    def pie_chart_ptype():
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            stm = "select count(sid) as count, ptype from rental_space, price group by ptype"
            cur.execute(stm)
            df = pd.DataFrame(cur.fetchall())
            fig = px.pie(df, values='count', names='ptype', title='Property type view')
            fig.show()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()

    @staticmethod
    def threed_bubble_chart_house_brief_overview():
        cnx = connect_db()
        cur = cnx.cursor()
        try:
            stm = "select sid, neighborhood, rate, person_capacity, ptype, daily_price from rental_space, price " \
                  "where rental_space.pid = price.pid"
            cur.execute(stm)
            df = pd.DataFrame(cur.fetchall())
            df["daily_price"] = df["daily_price"].apply(float)
            fig = px.scatter_3d(df, x='ptype', y='neighborhood', z='person_capacity', size='daily_price',
                                color='daily_price',
                                hover_data=['sid'])
            fig.update_layout(scene_zaxis_type="log")
            fig.show()
        except Exception as e:
            cnx.rollback()
            print(e)
        finally:
            cur.close()
            cnx.close()


# About Page
class AboutPage:
    def __init__(self, parent_window):
        parent_window.destroy()

        self.window = Tk()
        self.window.title('About')
        centralize_window(self.window)

        Label(text='Airbnb Info', bg='sky blue', font=('Verdana', font_size), width=30, height=2).pack()

        Label(text='''Author: Fengyi Quan \n        Anni Yuan \n         Wanqi Peng''',
              font=('Verdana', font_size)).pack(pady=30)

        Button(text="Back", width=8, font=font_size, command=self.back).pack(pady=100)

        self.window.protocol("WM_DELETE_WINDOW", self.back)
        self.window.mainloop()

    def back(self):
        StartPage(self.window)


if __name__ == '__main__':
    # read_load_data()
    StartPage(Tk())
