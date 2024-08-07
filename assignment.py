import pandas as pd
import openai
from flask import Flask, request, jsonify, send_from_directory

file_path = 'Wells.xlsx'
data = pd.read_excel(file_path, sheet_name='Wells Header Table')
data.fillna('Unknown', inplace=True)
data['Well Name'] = data['Well Name'].str.lower()
data['Field'] = data['Field'].str.lower()
data['Asset'] = data['Asset'].str.lower()
data['Pad Name'] = data['Pad Name'].str.lower()

print("Data loaded and preprocessed successfully.")
print("Sample data:")
print(data.head())

openai_api_key = 'API-key'
openai.api_key = openai_api_key

app = Flask(__name__)

def search_wells(query):
    query = query.lower()
    print(f"Processing query: {query}")
    
    if "details of well" in query:
        well_name = query.split("details of well")[-1].strip()
        print(f"Searching for well name: {well_name}")
        well_info = data[data['Well Name'].str.contains(well_name)]
        if well_info.empty:
            return None, f"No details found for well '{well_name}'."
        else:
            well_info = well_info.iloc[0]
            return {
                'latitude': well_info['Latitude'],
                'longitude': well_info['Longitude']
            }, None
    elif "show me all wells in" in query:
        if "asset" in query:
            asset = query.split("show me all wells in")[-1].split("asset")[0].strip()
            print(f"Searching for asset: {asset}")
            results = data[data['Asset'].str.contains(asset)]
        elif "field" in query:
            field = query.split("show me all wells in")[-1].split("field")[0].strip()
            print(f"Searching for field: {field}")
            results = data[data['Field'].str.contains(field)]
        elif "pad" in query:
            pad = query.split("show me all wells in")[-1].split("pad")[0].strip()
            print(f"Searching for pad: {pad}")
            results = data[data['Pad Name'].str.contains(pad)]
        else:
            return None, "Please specify whether you are looking for wells in an asset, field, or pad."

        if results.empty:
            print(f"No wells found in {asset or field or pad}.")
            return None, f"No wells found in {asset or field or pad}."
        else:
            wells_info = [
                {
                    'well_name': row['Well Name'],
                    'latitude': row['Latitude'],
                    'longitude': row['Longitude']
                }
                for _, row in results.iterrows()
            ]
            return wells_info, None
    else:
        return None, "Please ask about specific wells, assets, fields, or pads."

@app.route('/query', methods=['POST'])
def handle_query():
    query = request.json.get('query')
    results, error = search_wells(query)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({'results': results})

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == "__main__":
    app.run(debug=True)
