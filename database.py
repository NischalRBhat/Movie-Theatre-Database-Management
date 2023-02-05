import mysql.connector
mydb = mysql.connector.connect(host="localhost", user="root", password="",database="movie_theatre")
c = mydb.cursor()

import streamlit as st
import pandas as pd
#import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from csv import DictWriter

def view_all_screening_movies():
    c.execute('SELECT S.movie_id,M.title,S.audi_id FROM screening S, movie M where S.movie_id = M.mid')
    data = c.fetchall()
    return data

def view_all_movies():
    c.execute('SELECT S.mid,S.title,S.director from movie S')
    data = c.fetchall()
    return data

def read_screen():
    result = view_all_screening_movies()
    # st.write(result)
    df = pd.DataFrame(result, columns=['Movie_id', 'Title', 'Auditorium No'])
    with st.expander("View all Screening movies"):
        st.dataframe(df)
    """with st.expander("Train Source"):
        task_df = df['Source'].value_counts().to_frame()
        task_df = task_df.reset_index()
        st.dataframe(task_df)"""

def read_movie():
    result = view_all_movies()
    df = pd.DataFrame(result, columns=['Movie ID','Title','Director'])
    with st.expander("View all movies"):
        st.dataframe(df)

def insert_movie(mid,title,director,cast,description,duration_min):
    c.execute('INSERT INTO movie(mid,title, director, cast, description, duration_min) VALUES(%s,%s,%s,%s,%s,%s)',
              (mid, title, director, cast, description, duration_min))
    mydb.commit()

def insert_reservation(screen_id,user_name,res_contact,reserved,paid,sid):
    c.execute('INSERT INTO reservation(screen_id,user_name,res_contact,reserved,paid,sid) VALUES(%s,%s,%s,%s,%s,%s)',
            (screen_id,user_name,res_contact,reserved,paid,sid))
    c.execute('INSERT INTO seat_reserved(seat_id,screen_id) VALUES (%s,%s)',(sid,screen_id))
    c.execute('Select A.cost from screening A where A.audi_id = \"{}\"'.format(screen_id))
    data = c.fetchall()
    data = [i[0] for i in data]
    c.execute('Update screening set earnings = earnings + {}  where audi_id = \"{}\" '.format(data[0],screen_id))
    mydb.commit()

def create_new_movie():
    admin_user = st.text_input("Enter User Admin: ")
    admin_password = st.text_input("Enter password: ")
    st.button("Submit")
    purpose = st.selectbox("Choose the purpose",["Add new movie","Update the screening details","Delete movie"])
    if(admin_user == "Arjun Bhat" and admin_password == "gandeeva"):
        #if(st.button("Submit")):
        if(purpose == "Add new movie"):
            col1, col2 = st.columns(2)
            with col1:
                movie_id = st.text_input("Movie id: ")
                movie_title = st.text_input("Movie Title:")
                movie_dir = st.text_input("Director: ")
                movie_dur = st.text_input("Duration: ")

            with col2:
                movie_cast = st.text_input("Cast")
                movie_descr = st.text_input("Description")

            if st.button("Add Movie Record"):
                insert_movie(movie_id,movie_title,movie_dir,movie_cast,movie_descr,movie_dur)
            st.success("Successfully added Movie record {}".format(movie_title))

        elif(purpose == "Update the screening details"):
            c.execute("SELECT A.mid from movie A")
            data = c.fetchall()
            data = [x[0] for x in data]

            movie = st.selectbox("Select movie to be updated",data)

            lists = [1,2,3,4,5]
            audi = st.selectbox("Select the auditorium to be updated",lists)

            costs = st.text_input("Enter the ticket cost")

            if(st.button("Update")):
                c.execute("Delete from reservation where screen_id = \"{}\"".format(audi))
                mydb.commit()

                c.execute("Select S.audi_id, M.mid, M.title, S.earnings from movie M, screening S where M.mid = S.audi_id and S.audi_id = \"{}\"".format(audi))
                df = c.fetchall()
                dictionary = {"Screen id":df[0][0], "Movie id":df[0][1],"Movie title":df[0][2], "Earnings":df[0][3]}
                with open('box_office.csv','a') as f_object:
                    dict_writer = DictWriter(f_object,fieldnames=dictionary.keys())
                    dict_writer.writerow(dictionary)
                    f_object.close
                c.execute("UPDATE screening set movie_id = \"{}\", cost = \"{}\", earnings = 0 where audi_id = \"{}\"".format(movie,costs,audi))
                mydb.commit()
            st.success("Updated successfully")

        elif(purpose == "Delete movie"):
            c.execute("SELECT A.title from movie A where A.mid not in (SELECT distinct B.movie_id from screening B)")
            data = c.fetchall()
            data = [x[0] for x in data]
            movie = st.selectbox("Movie to be deleted",data)

            if(st.button("Delete")):
                c.execute("DELETE from movie where title = \"{}\"".format(movie))
                mydb.commit()
            st.success("Deleted successfully")

    else:
        st.error("Only Admin can add movies")


def auditoriums_seats():
    """auditorium_name = st.text_input("Auditorium Name")
    seat_id = st.text_input("Seat No")
    st.button("Submit")"""

    c.execute('SELECT A.name,count(B.seat_id),A.seats_no, C.title from auditorium A, seat_reserved B, movie C, screening D where A.aid = B.screen_id AND A.aid = D.audi_id AND C.mid = D.movie_id group by A.name')
    data = c.fetchall()

    df = pd.DataFrame(data, columns=['Auditorium Name', 'No of reserved seats', 'Total No of seats','Movie Running'])
    with st.expander("View all Reserved seats per auditorium"):
        st.dataframe(df)


def user_login():
    st.subheader("Step 1: Enter the Login Details")
    login_user = st.text_input("Username")
    login_passwd = st.text_input("Password")
    c.execute("SELECT U.username, U.passwords from users U")
    data = c.fetchall()
    count = 0
    st.button("Login")
    if (login_user,login_passwd) in data:
        st.success("Successfully logged in")
        st.subheader("Step 2: Enter the movie you want to watch")
        c.execute("SELECT DISTINCT A.title from movie A, screening B where A.mid = B.movie_id")
        movies_list = c.fetchall()
        movies_list = [x[0] for x in movies_list]
        val = st.selectbox("Currently Screening Movies", movies_list)

        st.subheader("Step 3: Enter auditorium to watch the movie in")
        c.execute("SELECT A.aid,C.cost from auditorium A, movie B, screening C where A.aid = C.audi_id and B.mid = C.movie_id and B.title = \"{}\"".format(val))
        audis_list = c.fetchall()
        #st.subheader(audis_list)
        audi_list = [x[0] for x in audis_list]
        cost_list = [x[1] for x in audis_list]
        val2 = st.selectbox("Auditorium the move is screening in: ",audi_list)
        ind = audi_list.index(val2)
        payment_cost = cost_list[ind]

        st.subheader("Step 4: Enter the seat No to book")
        c.execute("Select A.sid from seats A,auditorium C where (A.sid,\"{}\") not in (select B.sid, B.screen_id from reservation B) and A.audid = C.aid and C.aid = \"{}\"".format(val2,val2))
        seat_list = c.fetchall()
        seat_list = [x[0] for x in seat_list]
        val3 = st.selectbox("Seats available: ",seat_list)

        st.subheader("Step 5: Payment")
        st.subheader("Checkout cost: {}".format(payment_cost))
        cont = st.text_input("Enter contact details")
        if(cont==""):
            st.error("Enter the contact details")
        elif(st.button("Pay")):
            insert_reservation(val2,login_user,cont,"1","1",val3)
            st.success("Successfully reserved seats")

    else:
        if login_user in [x[0] for x in data]:
            st.error("Wrong Password. Please enter again")
        else:
            st.error("No such account found. Please enter correct credentials or register if there is no account")

def plot_pie():
    c.execute("Select A.name, RESERVED_SEATS(A.aid) as Reserved_seats from auditorium A")
    df = c.fetchall()
    df = dict(df)
    fig_target = go.Figure(data=[go.Pie(labels=list(df.keys()),
                                        values=list(df.values()),
                                        hole=.3)])
    fig_target.update_layout(showlegend=False,
                             height=200,
                             margin={'l': 20, 'r': 60, 't': 0, 'b': 0})
    fig_target.update_traces(textposition='inside', textinfo='label+percent')
    st.plotly_chart(fig_target, use_container_width=True)
    #st.subheader(df)
    #fig = px.pie(df, values=df.values)
    #fig.show()

def plot_movies():
    c.execute("Select M.title,count(*) from movie M, screening S, reservation R where M.mid = S.movie_id and S.audi_id = R.screen_id group by M.mid")
    data = c.fetchall()
    data = dict(data)
    fig_target = go.Figure(data=[go.Pie(labels=list(data.keys()),
                                        values=list(data.values()),
                                        hole=.3)])
    fig_target.update_layout(showlegend=False,
                             height=200,
                             margin={'l': 20, 'r': 60, 't': 0, 'b': 0})
    fig_target.update_traces(textposition='inside', textinfo='label+percent')
    st.plotly_chart(fig_target, use_container_width=True)
    #st.subheader(data)


def plot_reservations():
    #c.execute("Select count(*), A.seats_no from reservation R, auditorium A where A.aid = R.screen_id group by R.screen_id")
    c.execute("Select count(*) from reservation R group by R.screen_id order by R.screen_id")
    booked = c.fetchall()
    booked = [x[0] for x in booked]
    #data = dict(data)
    c.execute("Select A.seats_no from auditorium A")
    #st.subheader(data)
    total = c.fetchall()
    total = [x[0] for x in total]
    #booked, total = data.keys(), data.values()
    #booked, total = list(booked), list(total)
    remain = [total[i] - booked[i] for i in range(len(booked))]
    #st.subheader(booked)
    #st.subheader(remain)
    label = ["Booked", "Remaining"]
    l, r = st.columns(2)
    for i in range(5):
        temp = [booked[i], remain[i]]
        fig_target = go.Figure(data=[go.Pie(labels=label,
                                            values=temp,
                                            hole=.3)])
        fig_target.update_layout(showlegend=False,
                                 height=200,
                                 width=200,
                                 margin={'l': 20, 'r': 60, 't': 0, 'b': 0})
        fig_target.update_traces(textposition='inside', textinfo='label+percent')
        if(i % 2 == 0):
            #st.subheader("Auditorium {}".format(i+1))
            l.plotly_chart(fig_target, use_container_width=True)
        else:
            #st.subheader("Auditorium {}".format(i + 1))
            r.plotly_chart(fig_target, use_container_width=True)

def cost_function():
    c.execute("Select S.audi_id,S.earnings from screening S order by S.audi_id")
    data = c.fetchall()

    df = pd.DataFrame(data, columns=['Auditorium No','Earnings'])
    with st.expander("View the box office collections per screen"):
        st.dataframe(df)

    c.execute("Select A.title, sum(S.earnings) from movie A, screening S where A.mid = S.movie_id group by S.movie_id")
    data = c.fetchall()

    df = pd.DataFrame(data, columns=['Movie Name', 'Earnings'])
    with st.expander("View the box office collections per movie"):
        st.dataframe(df)

def insert_new_user(username, password):
    c.execute("Insert into users values(\"{}\",\"{}\")".format(username,password))
    mydb.commit()

def user_register():
    username = st.text_input("Enter new user name")
    password = st.text_input("Enter the password")

    try:
        if(st.button("Register")):
            insert_new_user(username,password)
            st.success("New User Registered! Move forward to reservations page")
    except:
        st.error("Username already exists")

