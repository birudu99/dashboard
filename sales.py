import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import base64
import altair as alt
import matplotlib.pyplot as plt

def sales(mydb):

    st.title('Sales')
    # css applied
    with open('C:/Users/91951/Desktop/dashboard app/static/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)

    # columns for partition
    col1, col2, col3, col4 = st.columns(4)

    ordersCount = "SELECT COUNT(order_id) as 'No Of Orders', sum(total_amount) as 'orders value', MONTHNAME(order_submit_dt_tm) as 'Month Name', YEAR(order_submit_dt_tm) as 'Year' FROM ecomm.orders GROUP BY month(order_submit_dt_tm) order by DATE(order_submit_dt_tm) desc"
    ordersDf = pd.read_sql(ordersCount, mydb)
    
    with col1:
        
        totalOrders = sum(ordersDf['No Of Orders'])
        st.metric("Orders To Date",totalOrders)

    with col2:
        
        cur_month = ordersDf['Month Name'].iloc[0]
        cur_sales = ordersDf['No Of Orders'].iloc[0]
        prev_month_sales = ordersDf['No Of Orders'].iloc[1]
        change_over_month=int(cur_sales-prev_month_sales)
        
        st.metric("Orders in "+cur_month,cur_sales,change_over_month)

    with col3:

        totalAmount = str(sum(ordersDf['orders value']))

        st.metric("Orders Value To Date", totalAmount+" "+u"\u20B9")

    with col4:
        st.subheader("Number of sales")
        st.metric("", "25%", "-8%")

    # columns for partition
    col10, col11 = st.columns(2)

    with col10:
        st.title("Orders Per Month")
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
        


        st.subheader("Percentage of Orders With Coupons")

        ordersCountByCoupon = ("SELECT coupon_applied, COUNT(order_id) as 'No Of Orders' "
                                "FROM ecomm.orders "
                                "GROUP BY coupon_applied")

        ordersCountByCouponDf = pd.read_sql_query(ordersCountByCoupon, mydb)

        labels = ordersCountByCouponDf['coupon_applied'].transform(lambda x: str(x)+' Coupon(s)')
        sizes = ordersCountByCouponDf['No Of Orders']

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        st.pyplot(fig1)

        '''optionSelect = st.multiselect("Coupon Applied", options= ordersCountByCouponDf['coupon_applied'].unique(), 
                                    default = ordersCountByCouponDf['coupon_applied'].unique())
        appliedCoupon = ordersCountByCouponDf.query("coupon_applied == @optionSelect")

        st.table(appliedCoupon)'''

    with col11:

        st.title("Trends in Products and Catagories")
        tab1, tab2 = st.tabs(["Products", "Catagories"])

        with tab1:
            productsInOrders = ("select sum(quantity) as 'Volume Ordered',product_name as Product from ecomm.order_item group by product_name order by sum(quantity) desc")
            productDf = pd.read_sql_query(productsInOrders, mydb)
            chart=alt.Chart(productDf).mark_bar().encode(
            y=alt.X('Product:N',sort=None),
            x='Volume Ordered',
            )
            st.altair_chart(chart,use_container_width=True)

        with tab2:
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


        salesByCatagories = (
        "SELECT o.order_id, DATE(o.order_submit_dt_tm) as ordered_date, ot.product_id, pc.catalog_id, "
        "ct2.catalog_name as categories, ct1.catalog_name as cata_products, COUNT(ct1.catalog_name) as no_of_sales "
        "FROM orders o "
        "LEFT JOIN order_item ot ON o.order_id = ot.order_id "
        "LEFT JOIN product_catalog_dir pc ON ot.product_id = pc.product_id "
        "LEFT JOIN catalog_dir ct1 ON pc.catalog_id = ct1.catalog_id "
        "LEFT JOIN catalog_dir ct2 ON ct1.parent_catalog_id = ct2.catalog_id "
        "GROUP BY cata_products ORDER BY cata_products")

        salesByCatagoriesDf = pd.read_sql_query(salesByCatagories, mydb)

        filterDf = salesByCatagoriesDf[['categories', 'no_of_sales']]

        salesByCatagoriesFilterDf1 = filterDf.groupby('categories')['no_of_sales'].agg(list).reset_index()

        salesByCatagoriesFilterDf1.columns = ['categories', 'sales']

        sales2 = salesByCatagoriesFilterDf1['sales']

        salesByCatagoriesFilterDf1['no of sales'] = sales2

        filterDf2 = salesByCatagoriesDf[['categories', 'cata_products']]

        salesByCatagoriesFilterDf2 = filterDf2.groupby('categories')['cata_products'].agg(list).reset_index()

        salesByCatagoriesFilterDf2.columns = ['categories', 'products']

        salesByCatagoriesFilterDf = pd.merge(salesByCatagoriesFilterDf2, salesByCatagoriesFilterDf1, on = 'categories')

        # salesByCatagoriesFilterDf1

        st.data_editor(
        salesByCatagoriesFilterDf,
        column_config={
            "sales": st.column_config.BarChartColumn(
                "sales",
                width="small",
                # help="The sales volume in the last 6 months",
                y_min=0,
                y_max=20,
                # color ='green', 
            )
        },
        hide_index=True,use_container_width=True
    )

    # columns for partition
    col7, col8, col9 = st.columns(3)

    with col7:
        st.subheader("Orders By Amount Range")

        ordersCountByTotalAmount5 = ("select COUNT(order_id) as 'No Of Orders' "
                                        "from ecomm.orders "
                                        "where orders.total_amount > 1000")

        ordersCountByTotalAmount4 = ("select COUNT(order_id) as 'No Of Orders' "
                                        "from ecomm.orders "
                                        "where orders.total_amount > 500 and orders.total_amount >= 1000")

        ordersCountByTotalAmount3 = ("select COUNT(order_id) as 'No Of Orders' "
                                        "from ecomm.orders "
                                        "where orders.total_amount > 300 and orders.total_amount >= 500")

        ordersCountByTotalAmount2 = ("select COUNT(order_id) as 'No Of Orders' "
                                        "from ecomm.orders "
                                        "where orders.total_amount > 100 and orders.total_amount >= 300")

        ordersCountByTotalAmount1 = ("select COUNT(order_id) as 'No Of Orders' "
                                        "from ecomm.orders where orders.total_amount <= 100")

        ordersCountByTotalAmountDf1 =  pd.read_sql_query(ordersCountByTotalAmount1, mydb)
        ordersCountByTotalAmountDf2 =  pd.read_sql_query(ordersCountByTotalAmount2, mydb)
        ordersCountByTotalAmountDf3 =  pd.read_sql_query(ordersCountByTotalAmount3, mydb)
        ordersCountByTotalAmountDf4 =  pd.read_sql_query(ordersCountByTotalAmount4, mydb)
        ordersCountByTotalAmountDf5 =  pd.read_sql_query(ordersCountByTotalAmount5, mydb)

        filteringData = [list(ordersCountByTotalAmountDf1['No Of Orders']), list(ordersCountByTotalAmountDf2['No Of Orders']), 
                    list(ordersCountByTotalAmountDf3['No Of Orders']), list(ordersCountByTotalAmountDf4['No Of Orders']), list(ordersCountByTotalAmountDf5['No Of Orders'])]
        ordersCountByTotalAmountDf = pd.DataFrame(filteringData)
        ordersCountByTotalAmountDf.columns = ['Orders']
        amountRange = ['<100 Rs', '101 - 300 Rs', '301 - 500 Rs', '501 - 1000 Rs', '>1000 Rs']
        ordersCountByTotalAmountDf['AmountRange'] = amountRange

        labels = amountRange
        sizes = ordersCountByTotalAmountDf['Orders']
        fig2, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        st.pyplot(fig2)

    with col8:
        None

    with col9:

        st.subheader('No Of Orders By Year')

        ordersCount = ("SELECT COUNT(order_id) as 'No Of Orders', order_id, DATE(order_submit_dt_tm) as 'Date', "
                        "DAY (order_submit_dt_tm) as 'Day', DAYNAME(order_submit_dt_tm) as 'Day Name', "
                        "MONTHNAME(order_submit_dt_tm) as 'Month Name', YEAR(order_submit_dt_tm) as 'Year' "
                        "FROM ecomm.orders GROUP BY DATE(order_submit_dt_tm)" )

        ordersDf = pd.read_sql(ordersCount, mydb)

        noOfOrdersCountDf = (ordersDf.groupby(['Year'])['No Of Orders'].sum()).reset_index()

        optionSelect = st.multiselect('select year', options=noOfOrdersCountDf['Year'].unique(), 
                                    default = noOfOrdersCountDf['Year'].unique())
        ordersByYearDf = noOfOrdersCountDf.query("Year == @optionSelect")

        st.bar_chart(ordersByYearDf, x='Year', y='No Of Orders')

    
    
    st.subheader("Average Customer Rating")
    query = """SELECT p.product_name, AVG(ps.avg_customer_rating) AS average_rating
                FROM product p
                JOIN product_sku ps ON p.product_id = ps.product_id
                WHERE ps.avg_customer_rating IS NOT NULL
                GROUP BY p.product_name
                ORDER BY AVG(ps.avg_customer_rating) DESC"""

    df = pd.read_sql(query, mydb)

    fig = px.bar(df, x='product_name', y='average_rating', title='Average Rating of Products')
    st.plotly_chart(fig, use_container_width=True)
