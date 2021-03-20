from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime
import pandas as pd
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return("Welcome to my api"
    f"Available Routes:<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"    
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/2015-03-06<br/>"
    f"/api/v1.0/2015-03-06/2016-11-09<br/>")
    # print("just stopping by to say 'hi!'")

@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Queries
    max_val = session.query(func.max(Measurement.date)).first()
    
    first_date = datetime.datetime.strptime(max_val[0], "%Y-%m-%d").date()
    last_date = first_date - pd.DateOffset(years=1)
    last_date = (last_date).date()
    
    annual_precip = session.query(Measurement.date, Measurement.prcp).\
                    filter(Measurement.date >= last_date).all()
    session.close()

   # Create a dictionary from the row data and append to a list of yearly_precip
    yearly_precip = []

    for date, prcp in annual_precip:
        rain_dict = {}
        rain_dict[date] = prcp
        # rain_dict["prcp"] = prcp
        yearly_precip.append(rain_dict)

    return jsonify(yearly_precip)

@app.route("/api/v1.0/stations")
def stat ():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Queries
    stations = session.query(Station.id, Station.station, Station.name).all()
    
    session.close()

    station_names =[]
    for id, station, name in stations:
        station_data ={}
        station_data["id"] = id
        station_data["station"] = station
        station_data["name"] = name
        station_names.append(station_data)
    
    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def temp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Queries
    max_val = session.query(func.max(Measurement.date)).first()
    
    first_date = datetime.datetime.strptime(max_val[0], "%Y-%m-%d").date()
    last_date = first_date - pd.DateOffset(years=1)
    last_date = (last_date).date()
    
    station_activity = session.query(Measurement.station, func.count(Measurement.station))\
                                .group_by(Measurement.station).order_by(Measurement.station.desc()).all()

    station_activity = sorted(station_activity, key=lambda x:x[1], reverse=True)
    station_id = station_activity[0][0]

    last_year_temp = session.query(Measurement.date, Measurement.station, Measurement.tobs).\
                    filter(Measurement.date >= last_date).\
                    filter(Measurement.station == station_id).all()
    session.close()

    observed_temp = []
    for date, station, tobs in last_year_temp:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["station"] = station
        temp_dict["temperature"] = tobs
        observed_temp.append(temp_dict)
    
    return jsonify(observed_temp)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Queries
    start_data = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                            filter(Measurement.date == start).all()
    session.close() 
    
    start_characteristics = []
    for min, max, avg in start_data:
        start_char = {}
        start_char["min_temp"] = min
        start_char["max_temp"] = max
        start_char["avg_temp"] = avg
        start_characteristics.append(start_char)

    return jsonify(start_characteristics)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Queries
    start_data = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                            filter(Measurement.date > start).\
                            filter(Measurement.date <= end).all()
    session.close()

    start_characteristics = []
    for min, max, avg in start_data:
        start_char = {}
        start_char["min_temp"] = min
        start_char["max_temp"] = max
        start_char["avg_temp"] = round(avg,2)
        start_characteristics.append(start_char)

    return jsonify(start_characteristics)

if __name__ == "__main__":
    app.run(debug=True)