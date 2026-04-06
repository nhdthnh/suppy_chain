import zipfile, os, xml.etree.ElementTree as ET

path = r"C:\Users\OQR\Desktop\supply_chain\templates\Pre-Order\LIEBU\0403_2026_OQR_LIEBU copy.xlsx"

# xlsx is a zip file - read sheet names directly from XML
with zipfile.ZipFile(path, 'r') as z:
    with z.open('xl/workbook.xml') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        sheets = root.find('main:sheets', ns)
        print("=== ALL SHEETS ===")
        for s in sheets.findall('main:sheet', ns):
            name = s.get('name')
            state = s.get('state', 'visible')
            sheet_id = s.get('sheetId')
            print(f"  Name='{name}', State='{state}', ID={sheet_id}")
