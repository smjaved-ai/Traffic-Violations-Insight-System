import streamlit as st
import mysql.connector as sql
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import jinja2

#connection func.
def get_connection():
    return sql.connect(
        host="172.21.144.1",
        user="py_user",
        password="qwe123QWE",
        database="dataset_traffic",
       )

def fetch_table(query,params=None):
    conn=get_connection()
    df=pd.read_sql(query,conn,params=params)
    conn.close()
    return df

def fetch_table2(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
      # Use cursor.execute directly; it handles %s safely
      cursor.execute(query, params)
      data = cursor.fetchall()
      # Get column names from the cursor description
      columns = [desc[0] for desc in cursor.description]
      return pd.DataFrame(data, columns=columns)
    finally:
         cursor.close()
         conn.close()

st.sidebar.title("Data Analysis")
option=st.sidebar.radio(
    "Navigate",("Home","Violations","Insights & charts","Summary & statistics")
)

if option=="Home":
        st.markdown("<h1 style='font-size:36px;'>Traffice Violation insight system</h1>",
        unsafe_allow_html=True)
        st.info("Traffic Insights Dashboard", icon="🚦", width="stretch")
        query="""select Make, Model, count(*) as Model_count
                  from traffic_violations where Accident=1 or ContributedToAccident="True"
                  group by Make, Model order by Model_count desc;"""
        vtype_acc_df=fetch_table(query).head(50)
        high_risk_df=fetch_table("select * from vio_by_location where Acc_count>10")
                       
        a, b = st.columns(2)
        
        a.metric(" 🛑 Total Violations", "488933", border=True)
        b.metric("💥 Violation with Accidents","20052",border=True)
        
        st.write("💀 High Risk Zone",unsafe_allow_html=True)
        
        chart5=px.bar(high_risk_df,x="location",y="Acc_count",
                     color="Acc_count",
                     labels={"location":"High Risk Location","Acc_count":"Accidents"})
        st.plotly_chart(chart5)

        st.markdown("<h1 style='font-size:18px;'>Common cited vehicle makes/models</h1>",unsafe_allow_html=True)
        st.table(vtype_acc_df,border=True)
        
elif option=="Violations":
     st.markdown("<h1 style='font-size:30px;'>📊Traffic Violation Insight</h1>",unsafe_allow_html=True)
     st.subheader("Multi-Filter View")
     col1, col2, col3, col4, col5, col6 = st.columns(6)
     with col1:
        conn=get_connection()
        cursor=conn.cursor()
        query= "SELECT DISTINCT YEAR(DateOfStop) FROM traffic_violations"
        cursor.execute(query)
        unique_list=[row[0] for row in cursor.fetchall()]
        unique_list.insert(0, "All")
        Year = st.selectbox("Year", unique_list)
        conn.close()
     with col2:
        conn=get_connection()
        cursor=conn.cursor()
        query= "SELECT DISTINCT DriverState FROM traffic_violations"
        cursor.execute(query)
        unique_list=[row[0] for row in cursor.fetchall()]
        unique_list.insert(0, "All")
        Driver_State = st.selectbox("DriverState", unique_list)
        conn.close()
     with col3:
        conn=get_connection()
        cursor=conn.cursor()
        query= "SELECT DISTINCT vehicletype FROM traffic_violations"
        cursor.execute(query)
        unique_list=[row[0] for row in cursor.fetchall()]
        unique_list.insert(0, "All")
        vehicle_type = st.selectbox("Vehicle Type", unique_list)
        conn.close()
     with col4:
        conn=get_connection()
        cursor=conn.cursor()
        query= "SELECT DISTINCT gender FROM traffic_violations"
        cursor.execute(query)
        unique_list=[row[0] for row in cursor.fetchall()]
        unique_list.insert(0, "All")
        gender = st.selectbox("Gender", unique_list)
        conn.close()
     with col5:
        conn=get_connection()
        cursor=conn.cursor()
        query= "SELECT DISTINCT race FROM traffic_violations"
        cursor.execute(query)
        unique_list=[row[0] for row in cursor.fetchall()]
        unique_list.insert(0, "All")
        race = st.selectbox("Race", unique_list)
        conn.close()
     with col6:
        conn=get_connection()
        cursor=conn.cursor()
        query= "SELECT DISTINCT violationtype FROM traffic_violations"
        cursor.execute(query)
        unique_list=[row[0] for row in cursor.fetchall()]
        unique_list.insert(0, "All")
        vio_type = st.selectbox("violation Type", unique_list)
        conn.close()

      # Filtered query   
        query = """
            SELECT YEAR(DateOfStop) as Year, DriverState, VehicleType, gender, Race, violationtype
            FROM traffic_violations 
            where 1=1
            """
        params=[]
        if Year != "All":
            query += " AND YEAR(DateOfStop) = %s"
            params.append(Year)

        if Driver_State != "All":
            query += " AND DriverState = %s"
            params.append(Driver_State)

        if vehicle_type != "All":
            query += " AND VehicleType = %s"
            params.append(vehicle_type)

        if gender != "All":
            query += " AND gender = %s"
            params.append(gender)

        if race != "All":
            query += " AND Race = %s"
            params.append(race)

        if vio_type != "All":
            query += " AND violationtype = %s"
            params.append(vio_type)
        query += " Limit 500"

        filtered_df = fetch_table(query,params=params)
            
     st.dataframe(filtered_df,hide_index=True)
         
elif option=="Insights & charts":
       st.header("Number of Accidents vs Year",divider="red")
       query="""SELECT YEAR(dateofstop) AS Year, COUNT(accident) AS Number_of_accidents
                FROM traffic_violations where accident=1 
                GROUP BY YEAR(dateofstop);"""
       year_acc_df=fetch_table(query)
       #st.dataframe(year_acc_df)
       chart1=px.line(year_acc_df,x="Year",y="Number_of_accidents",markers=True)
       st.plotly_chart(chart1)

       st.header("Number of Accidents vs Vehicle Type",divider="red")
       query="""SELECT vehicletype AS v_type, COUNT(accident) AS Number_of_accidents
                FROM traffic_violations where accident=1 
                GROUP BY vehicletype;"""
       vtype_acc_df=fetch_table(query)
       chart2=px.bar(vtype_acc_df,x="v_type",y="Number_of_accidents",
                     color="Number_of_accidents",
                     labels={"v_type":"Vehicle Type","Number_of_accidents":"Nos_of_accidents"})
       st.plotly_chart(chart2)

       st.header("Violation Type-Common Violation",divider="red")
       query="""SELECT violationtype AS vi_type, COUNT(accident) AS Number_of_accidents
                FROM traffic_violations where accident=1 
                GROUP BY violationtype;"""
       vitype_acc_df=fetch_table(query)
       chart3=px.pie(vitype_acc_df,values="Number_of_accidents",names="vi_type",labels={"vi_type":"Violation Type","Number_of_accidents":"Nos Of Accidents"})
       st.plotly_chart(chart3)
       
       st.header("Fatality vs Time Bucket",divider="red")
       query="""SELECT time_bucket AS time, COUNT(Fatal) AS Fatality
                FROM traffic_violations where Fatal=1 
                GROUP BY time_bucket;"""
       fat_time_df=fetch_table(query)
       chart4=px.bar(fat_time_df,x="time",y="Fatality",
                     color="Fatality",
                     labels={"time":"Time Bucket","Fatality":"Fatality"})
       st.plotly_chart(chart4)

elif option=="Summary & statistics":
      st.header("Statistical Data",divider="red")
      st.badge("Areas with Highest Number of Traffic Incidents",icon="🚨",color="red")
      vio_loc_df=fetch_table("select * from vio_by_location limit 100")
      st.dataframe(vio_loc_df,hide_index=True)

      st.badge("violations involve accidents, injuries or damage",icon="⚠️",color="orange")
      vio_view_df=fetch_table("""select violationType,
                  case when accident=1 then "Yes" else "No" end as Accident_Status, 
                  case when PersonalInjury=1 then "Yes" else "No" end as PersonalInjury,
                  case when PropertyDamage=1 then  "Yes" else "No" end as propertyDamage
                  from violations_view limit 100""")
      st.dataframe(vio_view_df,hide_index=True)

      st.badge("Demographics Data",icon="ℹ️",color="gray")
      vio_gender_df=fetch_table("select * from vio_by_gender")
      st.dataframe(vio_gender_df,width="stretch",hide_index=True)
                     
      vio_race_df=fetch_table("select * from vio_by_race")
      st.dataframe(vio_race_df,width="stretch",hide_index=True)