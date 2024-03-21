import pickle
from pathlib import Path
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth
from streamlit import session_state as state
import evadella_mysql
import base64

from summary import summary
from operations import operations
from sales import sales
from inventory import inventory
from staff_metrics import staff_metrics



st.set_page_config(
    page_title="EvaDella App",
    page_icon=":ring:",
    layout="wide",  
    initial_sidebar_state="collapsed",
    # background_color = "green",
    # background_image = "Task\iStock.jpg"
)

@st.cache_data
def get_image_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_image_as_base64("holder.jpg")

page_bg_img = """
    <style>
    [data-testid="stAppViewContainer"]{
    # background-color: #cfe8eb;
    background-image: url("data:image/png;base64,{img}");
    background-size: cover;
    }

    [data-testid="stHeader"]{
    background-color: rgba(0, 0, 0, 0);
    }

    </style>
    """

st.markdown(page_bg_img, unsafe_allow_html=True)

# user authentication
names = ["Giridhar", "Yerra"]
usernames = ["evadellagiri", "evadellayerra"]

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

    credentials = {
        "usernames":{
            usernames[0]:{
                "name":names[0],
                "password":hashed_passwords[0]
                },
            usernames[1]:{
                "name":names[1],
                "password":hashed_passwords[1]
                }           
            }
        }

#file_loc ='C:/Users/91951/Desktop/dashboard app/static/'

authenticator = stauth.Authenticate(credentials,
    "dashborad", "abcdefg", cookie_expiry_days = 30)

name, authentication_status, username = authenticator.login("login", "main")

if authentication_status == False:
    st.error("Username/Password is incorrect")

if authentication_status: 
    state.authentication_status = True
    # st.balloons()
    # st.snow()

    #instance of database
    db=evadella_mysql.db_instance()
    mydb=db.mydb

    st.title('📊 EvaDella App Dashboard')   # :bar_chart:

    authenticator.logout("logout")

    # Navigation Bar

    selected = option_menu(
        menu_title = None,
        options = ["Summary", "Operations", "Sales", "Inventory", "Staff Metrics"],
        icons = ["house", "", "book", "building", "person"],
        orientation = "horizontal",
    )

    if selected == "Summary":
        summary(mydb)

    if selected == "Operations":
        operations(mydb)

    if selected == "Sales":
        sales(mydb)   

    if selected == "Inventory":
        inventory(mydb)

    if selected == "Staff Metrics":
        staff_metrics(mydb)
