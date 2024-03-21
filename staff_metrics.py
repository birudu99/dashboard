import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def staff_metrics(mydb):

    st.title('Staff metrics') 

        # css applied
    with open('C:/Users/91951/Desktop/dashboard app/static/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)


    
    col1,col2,col2_1 = st.columns(3)

    with col1:

        staffCount='''SELECT COUNT(*) AS total_staff_count
                        FROM op_staff'''
        sCdf=pd.read_sql_query(staffCount,mydb)
        st.metric('Total Staff Count',sCdf['total_staff_count'].iloc[0])

    with col2:

        TurnOverRate='''SELECT COUNT(op_staff_id) AS staff_count,
                        SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), start_dt) > 365 THEN 1 ELSE 0 END) AS new_staff_count,
                        (SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), start_dt) > 365 THEN 1 ELSE 0 END) / COUNT(op_staff_id)) * 100 AS turnover_rate
                        FROM op_staff'''
        TOdf=pd.read_sql_query(TurnOverRate,mydb)
        st.metric("Staff Turnover Rate",TOdf['turnover_rate'].iloc[0])

    with col2_1:
        avgtime='''SELECT
                    AVG(ABS(TIMESTAMPDIFF(HOUR, o.last_update_dt_tm, os_prev.last_update_dt_tm))) AS avg_completion_time_minutes
                    FROM order_status o
                    JOIN op_staff os ON o.staff_cd = os.staff_cd
                    LEFT JOIN 
                    order_status os_prev ON o.order_id = os_prev.order_id AND os_prev.status_cd IN ('SHIPPING IN PROGRESS', 'SHIPPED','FILLING IN PROGRESS'
                    ,'FILLED','QC IN PROGRESS','QC SUCCESS','PACKING IN PROGRESS','PACKING DONE');'''

        atdf=pd.read_sql_query(avgtime,mydb)

        st.metric("Average Task completion Time","%0.2f"%atdf.iloc[0] + " Hours")


    col3,col4=st.columns(2)

    with col3:

        st.subheader("Target Orders Given To Staff")

        ordersByStaffAction = ("SELECT os.staff_cd, s.staff_name, DATE(os.last_update_dt_tm) as Date, "
                                "COUNT(os.order_id) as orderscount, opr.staff_role "
                                "FROM order_status os "
                                "LEFT JOIN op_staff s ON os.staff_cd = s.staff_cd "
                                "LEFT JOIN op_staff_role r ON s.op_staff_id = r.op_staff_id "
                                "LEFT JOIN op_role opr ON r.role_id = opr.role_id "
                                "GROUP BY os.staff_cd")

        ordersByStaffActionDf = pd.read_sql(ordersByStaffAction, mydb)
        thresholdData = pd.read_excel('C:/Users/91951/Desktop/dashboard app/static/sample_data.xlsx')

        threshold_dict = dict(zip(thresholdData['Name'], thresholdData['Threshold Value']))

        def color_status_cd(row):
            styles = ['color: green' if row['staff_cd'] in threshold_dict and row['orderscount'] >= threshold_dict[row['staff_cd']] else 'color: red'] * len(row)
            return styles

        styled_table = ordersByStaffActionDf.copy()
        styled_table = styled_table.style.apply(color_status_cd, axis=1)

        st.dataframe(styled_table)

    with col4:

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




    performance='''SELECT os.staff_name AS "Staff Name",
                    AVG(ABS(TIMESTAMPDIFF(HOUR, o.last_update_dt_tm, os_prev.last_update_dt_tm))) AS "Average Time(Hours)"
                    FROM order_status o
                    JOIN op_staff os ON o.staff_cd = os.staff_cd
                    LEFT JOIN 
                    order_status os_prev ON o.order_id = os_prev.order_id AND os_prev.status_cd IN ('SHIPPING IN PROGRESS', 'SHIPPED','FILLING IN PROGRESS'
                    ,'FILLED','QC IN PROGRESS','QC SUCCESS','PACKING IN PROGRESS','PACKING DONE')
                    GROUP BY os.staff_cd, os.staff_name'''

    pdf=pd.read_sql_query(performance,mydb)

    pdf['Color'] = ['red' if count > 30 else 'green' for count in pdf['Average Time(Hours)']]



    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=pdf['Staff Name'],
        y=pdf['Average Time(Hours)'],
        marker_color=pdf['Color'],
        name='Average Task Completion Time of Staff'
    ))


    fig.update_layout(
        title="Average Task Completion Time of Staff",
        xaxis_title='Staff Name',
        yaxis_title='Average Time(Hours)',
        legend=dict(title='Stock Count', title_font=dict(size=14, family="Arial, sans-serif"))
    )

    st.plotly_chart(fig, use_container_width=True)


    staffcount='''SELECT DATE(start_dt) AS date, COUNT(*) AS staff_count
                    FROM op_staff
                    WHERE YEAR(start_dt) = 2023
                    GROUP BY DATE(start_dt);'''

    sCdf = pd.read_sql_query(staffcount,mydb)

    sCdf['date']=pd.to_datetime(sCdf['date'])

    fig = px.bar(sCdf, x='date', y='staff_count', labels={'date': 'Date', 'staff_count': 'Staff Count'}, 
                title='Number of Staff Joined in 2023')

    # Adjust layout
    fig.update_layout(xaxis_title='Date', yaxis_title='Staff Count', 
                    xaxis={'categoryorder':'total ascending'}, # Sorting x-axis categories by total count
                    bargap=0.1, # Gap between bars
                    plot_bgcolor='rgba(0,0,0,0)', # Transparent plot background
                    )

    st.plotly_chart(fig, use_container_width=True)



