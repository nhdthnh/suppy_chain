import mysql.connector
import os
import sys

# Standard parser if toml not available, can use regular expression for simple format
def load_secrets():
    secrets = {}
    path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
    if not os.path.exists(path):
         return None
    with open(path, "r", encoding="utf-8") as f:
         content = f.read()
    
    # Simple parsing for secrets.toml
    # [mysql]
    # host = "..."
    # port = 3306
    current_section = None
    for line in content.splitlines():
         line = line.strip()
         if line.startswith("[") and line.endswith("]"):
              current_section = line[1:-1]
              secrets[current_section] = {}
         elif "=" in line and current_section:
              k, v = line.split("=", 1)
              k = k.strip()
              v = v.strip().strip('"').strip("'")
              if v.isdigit():
                   v = int(v)
              secrets[current_section][k] = v
    return secrets

try:
    sec = load_secrets()
    if not sec or "mysql" not in sec:
         print("No mysql configuration found in secrets.toml")
         sys.exit(1)
         
    cfg = sec["mysql"]
    conn = mysql.connector.connect(
         host=cfg["host"],
         port=cfg.get("port", 3306),
         user=cfg["user"],
         password=cfg["password"],
         database=cfg["database"]
    )
    
    cur = conn.cursor()
    cur.execute("SHOW TABLES")
    tables = [r[0] for r in cur.fetchall()]
    
    with open("db_size_output.txt", "w", encoding="utf-8") as f:
         f.write(f"Found tables: {tables}\n")
         total_rows = 0
         for t in tables:
              cur.execute(f"SELECT COUNT(*) FROM `{t}`")
              cnt = cur.fetchone()[0]
              f.write(f"Table {t}: {cnt} rows\n")
              total_rows += cnt
         f.write(f"Total rows: {total_rows}\n")
    print("Done")
    cur.close()
    conn.close()
except Exception as e:
    with open("db_size_output.txt", "w", encoding="utf-8") as f:
         f.write(f"Error: {str(e)}\n")
    print(f"Error: {e}")
