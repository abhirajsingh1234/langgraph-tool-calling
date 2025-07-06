import pyodbc

def execute_sql_query(query: str) -> list:
    """
    Executes a SQL SELECT query on the SQL Server and returns the results as a list of dicts.
    
    Parameters:
        query (str): A SELECT query string.
    
    Returns:
        List[dict]: List of rows as dictionaries.
    """
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=216.48.191.98;"
        "DATABASE=Credit_OPS_Main;"  # or Kredit_Bee_FC based on query
        "UID=ibsadmin;"
        "PWD=Viking@@ibs2023;"
    )

    try:
        with pyodbc.connect(conn_str, autocommit=True) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            results = [dict(zip(columns, row)) for row in rows]
            print(f"✅ Query executed successfully. Rows fetched: {len(results)}")
            return results
    except Exception as e:
        print(f"❌ Error executing query: {e}")
        return []
