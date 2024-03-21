import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt

def operations(mydb):
    
    st.title('Operations')
        # css applied
    with open('C:/Users/91951/Desktop/dashboard app/static/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)

    col1,col2,col3,col4 =st.columns(4)

    with col1:
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

    with col2:
        QCsuc=("SELECT COUNT(order_track_ref) as suc FROM ecomm.order_status WHERE status_cd='QC SUCCESS'")
        tOrder=("SELECT COUNT(order_id) as tot FROM orders")

        Qdf=pd.read_sql_query(QCsuc,mydb)
        tdf=pd.read_sql_query(tOrder,mydb)
        
        val= (Qdf['suc']/tdf['tot'])*100
        
        st.metric('QC Success Rate', value ="%.2f" %val+"%")

    with col3:
        QCfal=("SELECT COUNT(order_track_ref) as suc FROM ecomm.order_status WHERE status_cd='QC FAILED'")
        Fdf=pd.read_sql_query(QCfal,mydb)
        
        val= (Fdf['suc']/tdf['tot'])*100
        
        st.metric('QC Failure Rate', value ="%.2f" %val+"%")    

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





    st.subheader("Order Status Distribution")

    manuStatus= ("select m.manufacturer_name, o.status, count(o.status) as status_count from order_item oi "
                    "left join orders o on oi.order_id= o.order_id "
                    "left join product p on oi.product_id=p.product_id "
                    "left join manufacturer m on p.manufacturer_id=m.manufacturer_id "
                    "group by p.manufacturer_id, o.status")

    manuStatusDf = pd.read_sql_query(manuStatus,mydb)


    fig = px.bar(manuStatusDf, x=manuStatusDf['manufacturer_name'], y=manuStatusDf['status_count'], color="status",
    labels={"status_count":"No of orders","manufacturer_name":"manufacturer"},
    color_discrete_map={"SHIPPED":"#86CE00","PAYMENT FAILED":"#AF0038","SUBMITTED":"#636EFA","OPEN":"#1F77B4",
                        "QC FAILED":"#EF553B","QC SUCCESS":"#B6E880"})

    st.plotly_chart(fig, use_container_width=True)


    col5, col6 = st.columns(2)

    with col5:

        st.subheader("Orders Status each Month")

        orderCountByStatus = ("SELECT DATE(order_track_update_time) as 'Date', status_cd, order_id "
                                "FROM ecomm.order_status "
                                "WHERE order_status.order_track_update_time != 0")

        OCSdf = pd.read_sql_query(orderCountByStatus, mydb)

        # Convert 'Date' column to datetime type
        OCSdf['Date'] = pd.to_datetime(OCSdf['Date'])

        processed_data = OCSdf.groupby(['Date', 'status_cd']).size().reset_index(name='Count')

        # Selectbox for selecting the month
        selected_month = st.selectbox("Select Month", sorted(set(processed_data['Date'].dt.to_period("M"))))

        # Convert the period-like object to datetime-like object
        selected_month_start = selected_month.to_timestamp()
        selected_month_end = (selected_month + 1).to_timestamp() - pd.Timedelta(days=1)

        # Filter data for the selected month
        filtered_data = processed_data[(processed_data['Date'] >= selected_month_start) & (processed_data['Date'] <= selected_month_end)]

        # Aggregate counts for each status in the selected month
        aggregated_data = filtered_data.groupby('status_cd')['Count'].sum().reset_index()

        fig = px.sunburst(aggregated_data, path=['status_cd'], values='Count',
                  title=f'Status Count for {selected_month}', color='status_cd',
                  labels={'Count': 'Status Count'})

        # Show the animated pie chart in the Streamlit app
        st.plotly_chart(fig)

    with col6:

        st.subheader("Orders By Order Status By Week, Month, Year")

        option = st.selectbox("",
        ('Year', 'Week', 'Month'))

        def week():

            ordersWithStatusWeek = (
                "SELECT DATE(order_track_update_time) as Ordered_date, "
                "order_id, status_cd, DATE(estimated_time) as Estimated_date, staff_cd "
                "FROM ecomm.order_status "
                "WHERE order_track_update_time >= CURDATE() - INTERVAL 1 WEEK"
            )

            orderStatusWeekData = pd.read_sql_query(ordersWithStatusWeek, mydb)
            def highlight_cell(val, column):
                if column == column == 'status_cd' and val == 'PAID':
                    return 'color: blue'
                elif column == 'status_cd' and val == 'Delivered':
                    return 'color: green'
                elif column == 'status_cd' and val == 'Shipped':
                    return 'color: yellow'
                elif column =='status_cd' and val != 'Delivered':
                    return 'color: red'
                else:
                    return ''

            orderStatusWeekDataDF = orderStatusWeekData.style.apply(lambda x: [highlight_cell(val, column) for val, column in zip(x, x.index)], axis=1)

            st.dataframe(orderStatusWeekDataDF)
            # st.write('You selected:', option)

        def month():

            ordersWithStatusMONTH = ("SELECT DATE(order_track_update_time) as Ordered_date, order_id, status_cd, "
                                        "DATE(estimated_time) as Estimated_date, staff_cd "
                                        "FROM ecomm.order_status "
                                        "WHERE  order_track_update_time >= CURDATE() - INTERVAL 1 MONTH")

            orderStatusMonthData = pd.read_sql_query(ordersWithStatusMONTH, mydb)
            def highlight_cell(val, column):

                if column == column == 'status_cd' and val == 'PAID':
                    return 'color: blue'
                elif column == 'status_cd' and val == 'Delivered':
                    return 'color: green'
                elif column == 'status_cd' and val == 'SHIPPED':
                    return 'color: yellow'
                elif column =='status_cd' and val != 'Delivered':
                    return 'color: red'
                else:
                    return ''

            orderStatusMonthDataDF = orderStatusMonthData.style.apply(lambda x: [highlight_cell(val, column) for val, column in zip(x, x.index)], axis=1)
            st.dataframe(orderStatusMonthDataDF)

        # def year():
        #     orderStatusYearData = pd.read_sql_query(ordersWithStatusYear, mydb)
        #     def highlight_cell(val, column):
        #         if column == 'status_cd' and val == 'PAID':
        #             return 'color: blue'
        #         elif column == 'status_cd' and val == 'Delivered':
        #             return 'color: green'
        #         elif column == 'status_cd' and val == 'Shipped':
        #             return 'color: yellow'
        #         elif column =='status_cd' and val != 'Delivered':
        #             return 'color: red'
        #         else:   
        #             return ''
        #     orderStatusYearDataDF = orderStatusYearData.style.apply(lambda x: [highlight_cell(val, column) for val, column in zip(x, x.index)], axis=1)

        def year():
            # Load the threshold data from Excel
            thresholdData = pd.read_excel('C:/Users/91951/Desktop/dashboard app/static/threshold_data.xlsx')

            ordersWithStatusYear = ("SELECT DATE(order_track_update_time) as Ordered_date, order_id, status_cd, "
                                    "DATE(estimated_time) as Estimated_date, staff_cd "
                                    "FROM ecomm.order_status "
                                    "WHERE (order_track_update_time != 0 OR last_update_dt_tm != 0) "
                                    "AND order_track_update_time >= CURDATE() - INTERVAL 1 YEAR")

            # Read the orders data from SQL query
            orderStatusYearData = pd.read_sql_query(ordersWithStatusYear, mydb)

            def highlight_cell(val, column):

                if column == 'status_cd' and val == 'PAID':
                    return 'color: ' + thresholdData.loc[(thresholdData['Name'] == "status_cd") & (thresholdData['Threshold Value'] == "blue"), 'Threshold Value'].values[0]
                elif column == 'status_cd' and val == 'Delivered':
                    return 'color: ' + thresholdData.loc[(thresholdData['Name'] == "status_cd") & (thresholdData['Threshold Value'] == "green"), 'Threshold Value'].values[0]
                elif column == 'status_cd' and val == 'SHIPPED':
                    return 'color: ' + thresholdData.loc[(thresholdData['Name'] == "status_cd") & (thresholdData['Threshold Value'] == "yellow"), 'Threshold Value'].values[0]
                elif column == 'status_cd' and val != 'Delivered':
                    return 'color:red'

                # elif column in thresholdData.columns:
                #     threshold = thresholdData.loc[(thresholdData['Column'] == column), 'Threshold'].values[0]
                #     if val >= threshold:
                #         return 'color: ' + threshold
                #     else:
                #         return ''

                else:
                    return ''

            orderStatusYearDataDF = orderStatusYearData.style.apply(lambda x: [highlight_cell(val, column) for val, column in zip(x, x.index)], axis=1)

            st.dataframe(orderStatusYearDataDF)

        option_function_map = {
            'Week' : week,
            'Month' : month,
            'Year' : year,
        }

        selected_function = option_function_map.get(option)
        if selected_function:
            selected_function()

        # Common return reasons
    return_reasons_query = "SELECT * FROM total_return"
    return_reasons_df = pd.read_sql_query(return_reasons_query, mydb)
    return_reasons_df['return_reason'].replace('', 'Other', inplace=True)
    return_reason_counts = return_reasons_df['return_reason'].value_counts()

    st.subheader("Return Reasons Distribution")
    fig = px.pie(return_reason_counts, values=return_reason_counts.values, names=return_reason_counts.index, title='Return Reasons Distribution')
    st.plotly_chart(fig)