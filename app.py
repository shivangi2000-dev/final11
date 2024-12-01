import streamlit as st
import pandas as pd
import psycopg2
from config import DATABASE_CONFIG

# Connect to PostgreSQL
@st.cache_resource
def get_connection():
    return psycopg2.connect(**DATABASE_CONFIG)

# Run a SQL query
def execute_query(query, fetch_data=True):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        if fetch_data:
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=columns)
        conn.commit()
        return "Query executed successfully!"
    except Exception as e:
        return f"Error: {e}"

# Main Streamlit app
def main():
    st.title("FIFA Football Database")
    tabs = ["Home", "CRUD Operations", "Analytics", "Custom SQL"]
    selected_tab = st.sidebar.radio("Navigate", tabs)

    # Home Tab
    if selected_tab == "Home":
        st.header("Welcome to the FIFA Football Database")
        st.write("""
            Explore the world of football with data from FIFA matches, teams, and leagues.
            Use the sidebar to navigate through CRUD operations, analytics, and custom SQL queries.
        """)

    # CRUD Operations
    elif selected_tab == "CRUD Operations":
        st.header("CRUD Operations")
        operation = st.selectbox("Choose an operation", ["Create", "Read", "Update", "Delete"])
        
        if operation == "Create":
            table = st.selectbox("Select Table", ["country", "league", "team", "matches"])
            if table == "country":
                country_id = st.number_input("Enter Country ID", step=1)
                name = st.text_input("Enter Country Name")
                if st.button("Add Country"):
                    query = f"INSERT INTO country (id, name) VALUES ({country_id}, '{name}')"
                    st.write(execute_query(query, fetch_data=False))
        
        elif operation == "Read":
            table = st.selectbox("Select Table", ["country", "league", "team", "matches"])
            if st.button("View Table"):
                query = f"SELECT * FROM {table}"
                st.dataframe(execute_query(query))

        elif operation == "Update":
            table = st.selectbox("Select Table", ["country", "league", "team", "matches"])
            if table == "country":
                country_id = st.number_input("Enter Country ID to Update", step=1)
                new_name = st.text_input("Enter New Country Name")
                if st.button("Update Country"):
                    query = f"UPDATE country SET name = '{new_name}' WHERE id = {country_id}"
                    st.write(execute_query(query, fetch_data=False))

        elif operation == "Delete":
            table = st.selectbox("Select Table", ["country", "league", "team", "matches"])
            if table == "country":
                country_id = st.number_input("Enter Country ID to Delete", step=1)
                if st.button("Delete Country"):
                    query = f"DELETE FROM country WHERE id = {country_id}"
                    st.write(execute_query(query, fetch_data=False))

    # Analytics
    elif selected_tab == "Analytics":
        st.header("Analytics")
        queries = {
            "Top 5 Leagues by Average Goals": """
                SELECT league.name AS league_name, AVG(matches.home_team_goal + matches.away_team_goal) AS avg_goals
                FROM league
                JOIN matches ON league.id = matches.league_id
                GROUP BY league.name
                ORDER BY avg_goals DESC
                LIMIT 5;
            """,
            "Most Profitable Teams": """
                SELECT team.team_long_name, SUM(matches.home_team_goal + matches.away_team_goal) AS total_goals
                FROM team
                JOIN matches ON team.team_api_id = matches.home_team_api_id OR team.team_api_id = matches.away_team_api_id
                GROUP BY team.team_long_name
                ORDER BY total_goals DESC
                LIMIT 5;
            """
        }
        query_name = st.selectbox("Select Query", list(queries.keys()))
        if st.button("Run Query"):
            result = execute_query(queries[query_name])
            st.dataframe(result)

    # Custom SQL Queries
    elif selected_tab == "Custom SQL":
        st.header("Custom SQL Query")
        sql_query = st.text_area("Enter your SQL query here")
        if st.button("Execute"):
            result = execute_query(sql_query)
            if isinstance(result, pd.DataFrame):
                st.dataframe(result)
            else:
                st.write(result)

if __name__ == "__main__":
    main()

 
