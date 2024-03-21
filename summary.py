import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import altair as alt
import matplotlib.pyplot as plt
from datetime import datetime
import xlrd

def summary(mydb):
    st.title("Dashboard Summary")
    
    col1, col2,col3,col4, col5, col6= st.columns(6)

    with col1:
        
        ordersCount = "SELECT COUNT(order_id) as 'No Of Orders', sum(total_amount) as 'orders value', MONTHNAME(order_submit_dt_tm) as 'Month Name', YEAR(order_submit_dt_tm) as 'Year' FROM ecomm.orders GROUP BY month(order_submit_dt_tm) order by DATE(order_submit_dt_tm) desc"
        ordersDf = pd.read_sql(ordersCount, mydb)
        cur_month = ordersDf['Month Name'].iloc[0]
        cur_sales = ordersDf['No Of Orders'].iloc[0]
        prev_month_sales = ordersDf['No Of Orders'].iloc[1]
        change_over_month=int(cur_sales-prev_month_sales)
        
        st.metric("Orders in "+cur_month,cur_sales,change_over_month)      
            
    with col2:
      
        totalAmount = str(sum(ordersDf['orders value']))
        st.metric("Orders Value To Date", totalAmount+" "+u"\u20B9")
    
    with col3:

        statusTime = ("select o.order_submit_dt_tm as ordering_time, s.order_track_update_time as fulfillemt_time from orders o "
        "inner join order_status s on o.order_id=s.order_id where s.status_cd = 'SHIPPED'")

        df = pd.read_sql_query(statusTime,mydb)


        # Convert string to datetime
        df['ordering_time'] = pd.to_datetime(df['ordering_time'])
        df['fulfillemt_time'] = pd.to_datetime(df['fulfillemt_time'])

        # Calculate fulfillment time
        df['Fulfillment Time'] = (df['fulfillemt_time'] - df['ordering_time']).dt.total_seconds() / (60*60*24)  # in days

        # Calculate and display average fulfillment time as a metric
        average_fulfillment_time = df['Fulfillment Time'].mean()
        delta_value = average_fulfillment_time - df['Fulfillment Time'].iloc[-1]
        st.metric('Avg Order Fulfillment Time', f'{average_fulfillment_time:.1f}'+" Days", delta = "%.1f" %delta_value, delta_color="inverse")

    with col4:

        processTime=("SELECT s1.order_id, s1.order_track_update_time as filling_time, s2.order_track_update_time as shipping_time FROM ecomm.order_status s1 "
        "join ecomm.order_status s2 ON s1.order_id=s2.order_id "
        "WHERE s1.status_cd='FILLING IN PROGRESS' AND s2.status_cd='SHIPPING IN PROGRESS' "
        "ORDER BY order_id")

        pTdf=pd.read_sql_query(processTime, mydb)

        pTdf['filling_time'] = pd.to_datetime(pTdf['filling_time'])
        pTdf['shipping_time'] = pd.to_datetime(pTdf['shipping_time'])

        # Calculate fulfillment time
        pTdf['process Time'] = (pTdf['shipping_time'] - pTdf['filling_time']).dt.total_seconds() / (60*60)  # in hours

        # Calculate and display average fulfillment time as a metric
        average_processing_time = pTdf['process Time'].mean()
        delta_value = average_processing_time - pTdf['process Time'].iloc[-1]
        st.metric('Avg Warehouse Processing Time', f'{average_processing_time:.1f}'+" Hours", delta = "%.1f" %delta_value, delta_color="inverse")
            

    with col5:

        TurnOverRatio = '''SELECT (SUM(oi.quantity) / COUNT(DISTINCT oi.order_id)) AS ratio
                            FROM order_item oi'''
        TORdf= pd.read_sql_query(TurnOverRatio,mydb)

        st.metric("Inventory Turn Over Ratio",TORdf['ratio'].iloc[0])
    

    with col6:

        staffCount='''SELECT COUNT(*) AS total_staff_count
                        FROM op_staff'''
        sCdf=pd.read_sql_query(staffCount,mydb)
        st.metric('Total Staff Count',sCdf['total_staff_count'].iloc[0])



    col10, col11 = st.columns(2)

    with col10:
        st.subheader("Orders Per Month")
        ordersbyMonth = ('''SELECT COUNT(order_id) as 'No Of Orders', sum(total_amount) as 'orders value', 
                            MONTHNAME(order_submit_dt_tm) as 'Month Name', YEAR(order_submit_dt_tm) as 'Year' 
                            FROM ecomm.orders GROUP BY month(order_submit_dt_tm) 
                            order by DATE(order_submit_dt_tm)''')
        ordersDf = pd.read_sql(ordersbyMonth, mydb)

        chart = alt.Chart(ordersDf).mark_line().encode(
            x=alt.X('Month Name:N',sort=None),
            y='No Of Orders',
            tooltip=['Month Name','No Of Orders']
        ).interactive()
        st.altair_chart(chart,use_container_width=True)

    with col11:
        st.subheader("Trends In Catagories")
        CatalogSales = (
        "SELECT o.order_id, DATE(o.order_submit_dt_tm) as ordered_date, ot.product_id, pc.catalog_id, "
        "ct2.catalog_name as categories, ct1.catalog_name as cata_products, COUNT(ct1.catalog_name) as no_of_sales "
        "FROM orders o "
        "LEFT JOIN order_item ot ON o.order_id = ot.order_id "
        "LEFT JOIN product_catalog_dir pc ON ot.product_id = pc.product_id "
        "LEFT JOIN catalog_dir ct1 ON pc.catalog_id = ct1.catalog_id "
        "LEFT JOIN catalog_dir ct2 ON ct1.parent_catalog_id = ct2.catalog_id "
        "GROUP BY categories ORDER BY no_of_sales desc")
            

        CatalogSalesDf = pd.read_sql_query(CatalogSales, mydb)
        chart=alt.Chart(CatalogSalesDf).mark_bar().encode(
        y=alt.X('categories:N',sort=None),
        x=alt.Y('no_of_sales', title="Volume Ordered"),
        )
        st.altair_chart(chart,use_container_width=True)


    col10, col11 = st.columns(2)

    with col10:

        mostSold = '''SELECT pi.product_name as "product name", COUNT(oi.order_item_id) AS "total units sold"
                    FROM order_item oi
                    JOIN product_sku ps ON oi.product_sku = ps.product_sku_id
                    JOIN product pi ON ps.product_id = pi.product_id
                    GROUP BY pi.product_name
                    ORDER BY COUNT(oi.order_item_id) DESC
                    LIMIT 5'''

        mSdf =pd.read_sql_query(mostSold,mydb)

        fig = px.bar(mSdf, x='product name', y='total units sold', title='Top Selling Products',color='total units sold',color_continuous_scale=px.colors.diverging.Temps_r)
        st.plotly_chart(fig, use_container_width=True)

    with col11:

            query = """SELECT p.product_name, AVG(ps.avg_customer_rating) AS average_rating
                        FROM product p
                        JOIN product_sku ps ON p.product_id = ps.product_id
                        WHERE ps.avg_customer_rating IS NOT NULL
                        GROUP BY p.product_name
                        ORDER BY AVG(ps.avg_customer_rating) DESC
                        LIMIT 5"""

            df = pd.read_sql(query, mydb)

            fig = px.bar(df, x='product_name', y='average_rating', title='Average Rating of Products',color='average_rating',color_continuous_scale=px.colors.diverging.balance_r)
            st.plotly_chart(fig, use_container_width=True)

    col10, col11 = st.columns(2)

    with col10:

        st.subheader("Order Distribution")

        def fetch_data(selected_statuses):
            statuses = "','".join(selected_statuses)
            query = f'''SELECT m.manufacturer_name, o.status, COUNT(o.status) AS status_count 
                        FROM order_item oi
                        LEFT JOIN orders o ON oi.order_id = o.order_id
                        LEFT JOIN product p ON oi.product_id = p.product_id
                        LEFT JOIN manufacturer m ON p.manufacturer_id = m.manufacturer_id
                        WHERE o.status IN ('{statuses}')
                        GROUP BY p.manufacturer_id, o.status
                        ORDER BY count(o.status) DESC'''
            return pd.read_sql_query(query, mydb)

        # Select box for choosing statuses
        selected_statuses = st.multiselect("Select statuses", ["SHIPPED", "QC SUCCESS", "QC FAILED", "OPEN"], default=["SHIPPED"])
        # Fetch data based on selected statuses
        manuStatusDf = fetch_data(selected_statuses)

        # Plotting
        if not manuStatusDf.empty:
            fig = px.bar(manuStatusDf, x='manufacturer_name', y='status_count', color="status",
                        labels={"status_count": "No of orders", "manufacturer_name": "manufacturer"},
                        color_discrete_map={"SHIPPED":"#86CE00","OPEN":"#1F77B4","QC FAILED":"#EF553B","QC SUCCESS":"#B6E880"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No data available for the selected statuses.")

    with col11:

        return_reasons_query = "SELECT * FROM total_return"
        return_reasons_df = pd.read_sql_query(return_reasons_query, mydb)
        return_reasons_df['return_reason'].replace('', 'Other', inplace=True)
        return_reason_counts = return_reasons_df['return_reason'].value_counts()

        fig = px.pie(return_reason_counts, values=return_reason_counts.values, names=return_reason_counts.index, title='Return Reasons Distribution')
        st.plotly_chart(fig)

        st.write("""This chart can further be analized to check who the manufactuerer is, 
                who processed its QC, how often this product is returned,and much more if the database had enough data which was linked to various tables.""")

    col10, col11 = st.columns(2)

    with col10:

        orderStaff = '''SELECT os.staff_cd, os.staff_name, COUNT(o.order_id) AS orders_handled
        FROM op_staff os
        LEFT JOIN order_status o ON os.staff_cd = o.staff_cd
        GROUP BY os.staff_cd, os.staff_name ORDER BY orders_handled DESC LIMIT 5'''

        oSdf=pd.read_sql_query(orderStaff,mydb)

        fig = px.bar(oSdf, x='staff_name', y='orders_handled', 
                labels={'staff_name': 'Staff Name', 'orders_handled': 'Orders Handled'},
                title='Number of Orders Handled by Each Staff Member')

        fig.update_layout(xaxis_title='Staff Name', yaxis_title='Orders Handled',
                        plot_bgcolor='rgba(0,0,0,0)', # Transparent plot background
                        )

        st.plotly_chart(fig)


    with col11:
        
        df = pd.read_excel('C:/Users/91951/Desktop/dashboard app/static/staffloginIOT.xlsx')
        st.subheader("Staff working analysis")
        st.dataframe(df,use_container_width=True)
