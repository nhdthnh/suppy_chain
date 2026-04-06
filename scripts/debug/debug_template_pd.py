import pandas as pd
import os

def debug_template():
    path = r"C:\Users\OQR\Desktop\supply_chain\templates\Pre-Order\LIEBU\0403_2026_OQR_LIEBU copy.xlsx"
    if not os.path.exists(path):
        print("Path not found")
        return
    
    try:
        # Load only the master data sheet
        df = pd.read_excel(path, sheet_name="master data", header=None)
        print("--- MASTER DATA RAW (Top 10) ---")
        print(df.head(10).to_string())
        
        print("\n--- COLUMN A TYPES & SAMPLES ---")
        for i, val in enumerate(df[0].head(10)):
            print(f"Row {i+1} [Col A]: {repr(val)}")
            
        print("\n--- COLUMN D TYPES & SAMPLES ---")
        for i, val in enumerate(df[3].head(10)):
            print(f"Row {i+1} [Col D]: {repr(val)}")
            
    except Exception as e:
        print(f"Error: {e}")

debug_template()
