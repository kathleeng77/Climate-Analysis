# import dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify
import datetime as dt

# set up database
engine = create_engine("sqlite:///data/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# save to table, create session link, and set up Flask
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)
app = Flask(__name__)

@app.route("/")
def home()):
    """List all available api routes."""
    return"""<!DOCTYPE><html><h1>List of all available Honolulu, HI API routes</h1><ul>
    <li>List of precipitation scores from the last year:<br><a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a></li>
    <li>JSON list of stations:<br><a href="/api/v1.0/stations">/api/v1.0/stations</a></li>
    <li>JSON list of temp observations from the last year:<br><a href="/api/v1.0/tobs">/api/v1.0/tobs</a></li>
    <li>JSON list of tmin, tmax, tavg for the date provided:<br>Replace &ltstart&gt with a date in Year-Month-Day format.<br><a href="/api/v1.0/2017-01-01">/api/v1.0/2017-01-01</a></li>
    <li>JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive:<br>Replace &ltstart&gt and &ltend&gt with a date in Year-Month-Day format.<a href="/api/v1.0/2017-01-01/2017-01-07">/api/v1.0/2017-01-01/2017-01-07</a></li>
    </ul></html>"""

@app.route("/api/v1.0/precipitation")
def precipitation():
    """List of precipitation scores from the last year"""
    # calculate the date 1 year ago from latest date in database
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.datetime.strptime(latest_date[0], "%Y-%m-%d") - dt.timedelta(days=365)
    
    # retrieve precipitation scores and convert to dictionary
    last_year = dict(session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= year_ago).all())
    return jsonify(last_year)

@app.route("/api/v1.0/stations")
def stations(): 
    """JSON list of stations"""
    # retrieve stations and convert to list
    stations =  list(np.ravel(session.query(Measurement.station).group_by(Measurement.station).all()))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs(): 
    """JSON list of temp observations from the last year"""
    # calculate year ago from latest date in database
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.datetime.strptime(latest_date[0], "%Y-%m-%d") - dt.timedelta(days=365)
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # retrieve temp observations and convert to list
    temps = list(session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all())
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
def start(start):
    """JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""
    # retrieve temp observations from start date given and convert to list
    start_date = list(session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all())
    return jsonify(start_date)

@app.route("/api/v1.0/<start>/<end>")
def between(start, end):
    """Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""
    # retrieve temp observations from start and end dates given and convert to list
    between_dates = list(session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all())
    return jsonify(between_dates)

if __name__ == '__main__':
    app.run(debug=True)