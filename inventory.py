import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import time

def inventory(mydb):
    
    st.title('Inventory')

    def stream_data():

        text='''These tables can be further optimized if the database had 
                timestamps for inventory for when the products are shipped in from the manufacturers.
                Further, we can gain insights into reliability of logistics from maufacturers side.'''

        for word in text.split(" "):
            yield word + " "
            time.sleep(0.02)
        
    st.write_stream(stream_data)

    # css applied
    with open('C:/Users/91951/Desktop/dashboard app/static/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)


    st.subheader('Stock Quantity By Categories')

    productsStock = ("SELECT c2.catalog_name AS categories, c1.catalog_name AS products, p.product_name, ps.product_sku_id, "
                    "ps.product_sku_cd, ps.price, ps.status, SUM(ps.count) AS stock_count "
                    "FROM product_sku ps, product p, product_catalog_dir pc, catalog_dir c1, catalog_dir c2 "
                    "WHERE ps.product_id = p.product_id AND p.product_id = pc.product_id "
                    "AND pc.catalog_id = c1.catalog_id AND c1.parent_catalog_id = c2.catalog_id "
                    "GROUP BY categories ORDER BY categories")

    productsStockDF = pd.read_sql_query(productsStock, mydb)

    productsStockByCateDF = productsStockDF[["categories", "stock_count"]]

    target_value = 5
    high_level = 45

    chart = alt.Chart(productsStockByCateDF).mark_line().encode(
        x='categories',
        y='stock_count',
        tooltip=['categories', 'stock_count'] # Adding 'tooltip' here will show these fields on hover
    )

    target_line = alt.Chart(pd.DataFrame({'target': [target_value]})).mark_rule(color='red').encode(
        y='target:Q'
    )

    high_level_line = alt.Chart(pd.DataFrame({'target': [high_level]})).mark_rule(color='green').encode(
        y='target:Q'
    )

 
    final_chart = chart + target_line + high_level_line

    st.altair_chart(final_chart, use_container_width=True)




    st.subheader("Sales count by products")

    stockCountByProducts = ("SELECT c.catalog_name AS products, SUM(ps.count) AS stock_count "
                            "FROM product_sku ps, product p, product_catalog_dir pc, catalog_dir c "
                            "WHERE ps.product_id = p.product_id AND p.product_id = pc.product_id "
                            "AND pc.catalog_id = c.catalog_id "
                            " GROUP BY products; ")

    stockCountByProductsDf = pd.read_sql_query(stockCountByProducts, mydb)

    stockCountByProductsDf['color'] = ['red' if count < 10 else 'green' for count in stockCountByProductsDf['stock_count']]


    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=stockCountByProductsDf['products'],
        y=stockCountByProductsDf['stock_count'],
        marker_color=stockCountByProductsDf['color'],
        name='Stock Count'
    ))

    fig.add_trace(go.Scatter(
        x=stockCountByProductsDf['products'],
        y=stockCountByProductsDf['stock_count'],
        mode='lines',
        line=dict(color='white', width=3),
        showlegend=False
    ))

    fig.update_layout(
        title="",
        xaxis_title="Product",
        yaxis_title="Stock Count",
        xaxis=dict(tickangle=45),
        yaxis=dict(range=[0, max(stockCountByProductsDf['stock_count']) + 5]),
        legend=dict(title='Stock Count', title_font=dict(size=14, family="Arial, sans-serif"))
    )

    st.plotly_chart(fig,use_container_width=True)





    orderQuant = ('''SELECT SUM(quantity) as 'No Of Products', 
                        MONTHNAME(o.order_submit_dt_tm) as 'Month', YEAR(o.order_submit_dt_tm) as 'Year' 
                        FROM ecomm.orders o 
                        LEFT JOIN ecomm.order_item oi ON o.order_id=oi.order_id
                        GROUP BY month(order_submit_dt_tm) 
                        order by DATE(order_submit_dt_tm)''')

    oQdf = pd.read_sql_query(orderQuant, mydb)

    stockQuant = ('''SELECT SUM(count) FROM ecomm.product_sku''')

    sQdf = pd.read_sql_query(stockQuant,mydb)

    sQdf['No Of Products'] = sQdf['SUM(count)'].iloc[0]  # Set the value for all rows in sQdf
    sQdf = pd.DataFrame(np.repeat(sQdf.values, len(oQdf), axis=0), columns=sQdf.columns)  # Repeat the rows

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=oQdf['Month'], y=oQdf['No Of Products'], mode='lines+markers',
                            name='Order Quantity'))

    fig.add_trace(go.Scatter(x=oQdf['Month'], y=sQdf['No Of Products'], mode='lines+markers',
                            name='Stock Quantity', line=dict(color='green')))

    fig.update_layout(title='Quantity Over Various Months',
                    xaxis_title='Month',
                    yaxis_title='Quantity')

    st.plotly_chart(fig,use_container_width=True)


    col1,col3,col4 =st.columns(3)
    
    with col1:

        TurnOverRatio = '''SELECT (SUM(oi.quantity) / COUNT(DISTINCT oi.order_id)) AS ratio
                            FROM order_item oi'''
        TORdf= pd.read_sql_query(TurnOverRatio,mydb)

        st.metric("Inventory Turn Over Ratio",TORdf['ratio'].iloc[0])

    
        inventoryAge='''SELECT CASE
        WHEN DATEDIFF(NOW(), ps.create_date) <= 30 THEN '0-30 days'
        WHEN DATEDIFF(NOW(), ps.create_date) <= 60 THEN '31-60 days'
        WHEN DATEDIFF(NOW(), ps.create_date) <= 90 THEN '61-90 days'
        ELSE 'More than 90 days'
        END AS inventory_age,
        COUNT(*) AS product_count
        FROM product_sku ps
        GROUP BY inventory_age'''

        iAdf =pd.read_sql_query(inventoryAge,mydb)

        st.metric("inventory over 90 days old", iAdf.iloc[0,1])

        with col3:
            
            def color_rows(val):
                if val == 'Over 90 days old':
                    color = 'red'
                elif val == '61-90 days old':
                    color = 'orange'
                elif val == '31-60 days old':
                    color = 'yellow'
                else:
                    color = 'green'
                return f'background-color: {color}'

            Product_age='''SELECT ps.product_sku_cd, CASE
                            WHEN DATEDIFF(NOW(), ps.create_date) > 90 THEN 'Over 90 days old'
                            WHEN DATEDIFF(NOW(), ps.create_date) > 60 THEN '61-90 days old'
                            WHEN DATEDIFF(NOW(), ps.create_date) > 30 THEN '31-60 days old'
                            ELSE '30 days or less old'
                            END AS age_category
                            FROM product_sku ps
                            WHERE DATEDIFF(NOW(), ps.create_date) > 30;'''

            pAdf = pd.read_sql_query(Product_age,mydb)
            styled_df = pAdf.style.applymap(color_rows, subset=['age_category'])

            st.subheader('Product Age Analysis')
            st.dataframe(styled_df)

        with col4:
            mostSold = '''SELECT pi.product_name as "product name", COUNT(oi.order_item_id) AS "total units sold"
                        FROM order_item oi
                        JOIN product_sku ps ON oi.product_sku = ps.product_sku_id
                        JOIN product pi ON ps.product_id = pi.product_id
                        GROUP BY pi.product_name
                        ORDER BY COUNT(oi.order_item_id) DESC
                        LIMIT 5'''

            mSdf =pd.read_sql_query(mostSold,mydb)

            fig = px.bar(mSdf, x='product name', y='total units sold', title='Top Selling Products')
            st.plotly_chart(fig, use_container_width=True)