from flask import Flask, jsonify, send_from_directory
from pymongo import MongoClient
from flask_cors import CORS
import pandas
import scipy.stats as sts

app = Flask(__name__, static_url_path='', static_folder='static')
CORS(app)  # Enable CORS for all routes

client_json = MongoClient("mongodb://localhost:27017/")
db_json = client_json["crime_db"] #Replace "crime_db" with your database name
collection= db_json.incidents #Replace "incidents" with your collection name
#(supposedly the final version of the cleaned sample data/not ready right now)
collection_full=db_json.incidents_full #Fully cleaned data, 500k+ rows

@app.route("/")
def home():
    return send_from_directory(app.static_folder, 'index.html')
@app.route("/about")
def about():
    return send_from_directory(app.static_folder, 'about.html')

@app.route("/page3")
def page3():
    return send_from_directory(app.static_folder, 'page3.html')

@app.route("/page4")
def page4():
    return send_from_directory(app.static_folder, 'page4.html')

@app.route("/page5")
def page5():
    return send_from_directory(app.static_folder, 'page5.html')

@app.route("/page6")
def page6():
    return send_from_directory(app.static_folder, 'page6.html')

@app.route("/data", methods=['GET'])
def get_full_data():
  
    cursor = collection_full.find()

    data = [{
        key: value for key, value in doc.items() if key != '_id'
    } for doc in cursor]

    return jsonify(data)

@app.route("/reduced_data", methods=['GET']) #end point for the final sample data
def get_reduced_data():
   
    cursor = collection.find()

    data = [{
        key: value for key, value in doc.items() if key != '_id'
    } for doc in cursor]

    return jsonify(data)

@app.route("/selected", methods=['GET']) #end point for the slected categories based on the final sample data
def get_selected_data():
 
    cursor = collection.find({}, {"Latitude": 1, 
                                  "Longitude": 1, 
                                  "Incident Datetime": 1, 
                                  "Incident Description": 1, 
                                  "Analysis Neighborhood": 1, 
                                  "Incident Category": 1, 
                                  "Incident Year": 1})

    data = [{
        key: value for key, value in doc.items() if key != '_id'
    } for doc in cursor]

    return jsonify(data)

## BL Update Start ##

def return_slope(input_y): 
    slope, intercept, r, p, std=sts.linregress(range(2018, 2025), input_y)
    return slope

@app.route("/selected_bl", methods=['GET']) #end point for the slected categories based on the final sample data
def get_selected_data_bl():
    cursor=collection.aggregate([
        { "$group": {
        "_id": {
            "Incident Category": "$Incident Category",
            "Incident Year": "$Incident Year"
        },
        "Count": { "$sum": 1 }
    }}])
                         
    data = [{'Incident Category': doc['_id']['Incident Category'], 'Incident Year': doc['_id']['Incident Year'], 'Count': doc['Count']} for doc in cursor]
    tmp=pandas.DataFrame(data)
    tmp=tmp.pivot(index='Incident Category', columns='Incident Year', values='Count')
    tmp=tmp.fillna(0)
    tmp=tmp.apply(lambda x:x/x.sum())
    results=(tmp.apply(return_slope, axis=1)*100).sort_values()
    return jsonify({'Category': list(results.index), 'Slope': list(results.values)})
    
## BL Update End ##

@app.route("/selected_<type>", methods=['GET']) #end point with option of viewing each category
def get_type_json(type):

    cursor = collection.find({"Incident Category": type}, {"Latitude": 1, 
                                  "Longitude": 1, 
                                  "Incident Datetime": 1, 
                                  "Incident Description": 1, 
                                  "Analysis Neighborhood": 1, 
                                  "Incident Category": 1, 
                                  "Incident Year": 1})

    data = [{
        key: value for key, value in doc.items() if key != '_id'
    } for doc in cursor]

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
