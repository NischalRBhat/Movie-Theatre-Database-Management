import mysql.connector
mydb = mysql.connector.connect(host="localhost", user="root", password="",database="movie_theatre")
c = mydb.cursor()

import streamlit as st
import base64
import plotly.express as px
from database import read_screen, read_movie, create_new_movie, auditoriums_seats, user_login, plot_pie, plot_movies, plot_reservations, cost_function, user_register

def bg_url(img_file):
    with open(img_file,"rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/{"jpg"};base64,{encoded_string.decode()});
            background-attachment: fixed;
            background-size: cover
        }}
        </style>
        """,
        unsafe_allow_html = True
    )

def main():
    #st.title("Welcome to Movie Theatre Andromeda")
    st.markdown('<h1 style = "color: Blue; text-shadow: 2px 2px #ff0000;"> Welcome to Andromeda Multiplex</h1>', unsafe_allow_html=True)
    menu = ["User Registration","Screening Movies","Reserve Ticket","Auditorium","Box Office Earnings"]
    choice = st.sidebar.selectbox("Menu",menu)
    bg_url('bgimg2.jpg')
    if choice == "User Registration":
        #st.subheader("Register as a new user")
        st.markdown('<h2 style = "color: Black; text-shadow: 2px 2px #ff0000;"> User Registration </h2>',
                    unsafe_allow_html=True)
        bg_url('blue.jpg')
        user_register()

    elif choice == "Screening Movies":
        #st.subheader("Currently Screening Movies")
        st.markdown('<h2 style = "color: Gold; text-shadow: 2px 2px #ff0000;"> Screening Movie Information </h2>', unsafe_allow_html=True)
        bg_url('light.jpg')
        read_screen()
        read_movie()
        st.subheader("Verify access to movie database")
        create_new_movie()
        read_screen()
        read_movie()

    elif choice == "Reserve Ticket":
        #st.subheader("Reserve a Ticket")
        st.markdown('<h2 style = "color: Silver; text-shadow: 2px 2px #ff0000;"> Reserve a ticket </h2>', unsafe_allow_html=True)
        bg_url('reserve.jpg')
        user_login()
    elif choice == "Auditorium":
        #st.subheader("Choose the auditorium")
        st.markdown('<h2 style = "color: Gold; text-shadow: 2px 2px #ff0000;"> Auditorium information </h2>',
                    unsafe_allow_html=True)
        auditoriums_seats()
        l,r = st.columns(2)
        with l:
            st.subheader("Booked seats distribution in screens")
            plot_pie()
        with r:
            st.subheader("Booked seats distribution for screening movies")
            plot_movies()
        #plot_users()
        st.subheader("Distribution of booked tickets in each screen")
        plot_reservations()
    elif choice == "Box Office Earnings":
        st.markdown('<h2 style = "color: Gold; text-shadow: 2px 2px #ff0000;"> Box office earnings </h2>', unsafe_allow_html=True)
        bg_url("lighter.jpg")
        cost_function()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
