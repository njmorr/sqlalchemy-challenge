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
    f"/api/v1.0/<start><br/>"
    f"/api/v1.0/<start>/<end><br/>")
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
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)


if __name__ == "__main__":
    app.run(debug=True)