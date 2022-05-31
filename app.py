#import python dependencies
import numpy as np
import pandas as pd
import datetime as dt

#import sqlalchemy dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

#import flask dependencies 
from flask import Flask, jsonify, json

# create engine to hawaii.sqlite
path = '/Users/anthonygarcia/Desktop/hawaii.sqlite'
engine = create_engine(f"sqlite:///{path}")

#delcare a base
Base = automap_base()

#reflect the database tables
Base.prepare(engine, reflect=True)

#assign measurement to variable
measure = Base.classes.measurement
station = Base.classes.station

#create a session
session = Session(engine)


#create an app
app = Flask(__name__)

#define the homepage
@app.route("/")

#add routing information for each of the routes
def welcome():
    return json.dumps(
        f"Welcome!<br/>"
        f"These are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        
    )

#create a precipitation route 
@app.route("//api/v1.0/precipitation")
def precipitation():

    #obtain the most recent date
    date = session.query(measure.date).order_by(measure.date.desc()).first()
    #get the precipitation data based on recent date for the past 12 months
    qry = session.query(measure.date,measure.prcp).filter(measure.date >= '2016-09-01').group_by(measure.date).order_by(measure.date.desc()).all()
    #create a dictionary with jsonify
    precip = {date:precip for date,precip in qry}
    session.close()
    return jsonify (precip)  


#create a station route
@app.route("/api/v1.0/stations")
def stations():
    #create a query to get all the stations
    station_ = session.query(station.station).all()
    #create a dictionary with jsonify
    session.close()
    return jsonify([dict(s) for s in station_])


#create a tobs route
@app.route("/api/v1.0/tobs")
def tobs():
#query the dates and temperature observations of the most active station for the previous year of data
    active_station = session.query(measure.date,measure.tobs).\
          filter(measure.station == 'USC00519281').\
          filter(measure.date >= '2016-09-01').\
          order_by(measure.date.desc()).all()
    #create a dictionary and print json list of temperature observations for the previous year
    session.close()
    return jsonify([dict(active) for active in active_station])

#create start and end routes
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

def stats(start,end):
    #query min, avg and max temperatures
    sum = [func.min(measure.tobs), func.avg(measure.tobs),func.max(measure.tobs)]
    #add in not statement to set the start and end date
    if not end:
        results = session.query(*sum).filter(measure.date >=start).filter(measure.date <=end).all()
        temps = list(np.ravel(results))
        session.close()
        return jsonify(temps)

    #calculate the results 
    results = session.query(*sum).filter(measure.date >=start).filter(measure.date <=end).all()
    temps = list(np.ravel(results))
    session.close()
    return jsonify(temps)


#define the main behavior
if __name__ == "__main__":
    app.run(debug=True)


   



