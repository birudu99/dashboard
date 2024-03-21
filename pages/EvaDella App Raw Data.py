import pandas as pd
import numpy as np
import streamlit as st
# import mysql.connector
from EvaDella_App import *
from evadella_mysql import *
# from evadellalogin import *
import streamlit_authenticator as stauth


st.set_page_config(
    page_title="EvaDella App",
    page_icon="🧊"
)

# css applied
with open('C:/Users/91951/Desktop/dashboard app/static/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)

if not hasattr(state, "authentication_status"):
    state.authentication_status = True

if not state.authentication_status:
    st.error("Please login with username/password")
    
else:
    st.title('Raw Data To Home Page')

        # authenticator.logout("logout")

    st.subheader('Total Orders Details')

    ordersCount = ("SELECT COUNT(order_id) as 'No Of Orders', order_id, DATE(order_submit_dt_tm) as 'Date', "
                    "DAY (order_submit_dt_tm) as 'Day', DAYNAME(order_submit_dt_tm) as 'Day Name', "
                    "MONTHNAME(order_submit_dt_tm) as 'Month Name', YEAR(order_submit_dt_tm) as 'Year' "
                    "FROM ecomm.orders "
                    "GROUP BY DATE(order_submit_dt_tm)" )

    # unShippedOrdersMonthCountDf1
    ordersDf = pd.read_sql(ordersCount, mydb)

    totalOrders = sum(ordersDf['No Of Orders'])

    st.metric("Total No Of Orders", totalOrders)

    st.dataframe(ordersDf)

                                                                                        