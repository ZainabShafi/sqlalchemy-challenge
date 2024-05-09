# Import the dependencies.
import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session 
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base =automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Save references to each table


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
#List all the available routes:

@app.route("/")
def welcome():
    return (
        f"<p>Here's my Hawaii Weather API!</p>"
        f"<p>Description:</p>"
        f"/api/v1.0/precipitation<br />A list of percipitation data between 8/23/16 and 8/23/17<br/><br/>"
        f"/api/v1.0/stations<br /> A list of weather stations and names<br/><br/>"
        f"/api/v1.0/tobs<br /> A list of temp observations from the most active station (2016-2017)<br/><br/>"
        f"<p> For the following app routes, specify date in MM-DD-YYYY format:<br/><br/>"
        f"/api/v1.0/start/<start_date><br /> A list of min, max and avg temps between a given start date and 8/23/17 <br /><br/>"
        f"<p>For route below separate each date with a / :<br/><br/>"
        f"/api/v1.0/start_end/<start>/<end> <br /> A list of min, max and avg temps between a given start and end date <br /><br/>"
        
    )

#Convert the query results from your precipitation analysis into a dict:

@app.route('/api/v1.0/precipitation')
def precipitation(): 
    year_b4 = dt.date(2017, 8, 24) - dt.timedelta(days=366)
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_b4).all()
    session.close()

    weather_data = []
    for date, prcp in data:
        weather_dict = {}
        weather_dict["date"] = date 
        weather_dict["prcp"] = prcp
        weather_data.append(weather_dict)

    return jsonify(weather_data)

#Return a JSON list of stations from the dataset:

@app.route("/api/v1.0/stations")
def stations(): 
    stations = session.query(Station.station, Station.name).all()
    
    session.close() 

    all_stations = list(np.ravel(stations))

    return jsonify(all_stations)

#Return a JSON list of temperature observations for the previous year, most active station:

@app.route("/api/v1.0/tobs")
def tobs():
    year_b4 = dt.date(2017, 8, 24) - dt.timedelta(days=366)
    temps = session.query(Measurement.tobs). \
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= year_b4).all()
    
    all_temps = list(np.ravel(temps))
    return jsonify(all_temps)


#For a specified start, calculate TMIN, TAVG, TMAX for all the dates greater than or equal to the start date:
@app.route("/api/v1.0/start/<start_date>")
#start_date is a dynamic parameter:
def start(start_date):
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    #spec_start var = temp(tobs) query with start_date specified
    spec_start = session.query(*sel).filter(Measurement.date >= start_date).all()

    #creating list of temp info for jsonification:
    spec_start_temps = []
    for row in spec_start:
        spec_start_temps.append({
            "min_temperature": row[0],
            "max_temperature": row[1],
            "avg_temperature": row[2]
        })

    return jsonify(spec_start_temps)

#For a specified start date and end date, calculate TMIN, TAVG, and TMAX:
@app.route("/api/v1.0/start_end/<start>/<end>")
#start, end are dynamic parameters:
def start_end(start,end):
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    dates = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

#start_end_temp = list of temp info from start to end date for jsonification:
#using forloop to append this list.
    start_end_temp = []
    for row in dates:
        start_end_temp.append({
            "min_temperature": row[0],
            "max_temperature": row[1],
            "avg_temperature": row[2]
        })

    return jsonify(start_end_temp)


if __name__ == "__main__":
    app.run(debug=True)
    