import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_

from flask import Flask, jsonify

#Here goes all of my variables

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base=automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)
beginning_date=session.query(Measurement.date).order_by(Measurement.date.asc()).first()
final_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
session.close()
beginning_date=beginning_date[0]
final_date=final_date[0]

#INITIALIZE THE FLASK APP
app=Flask(__name__)

#ROUTES
@app.route("/")
def home():
    return f"""
    <h1 font-size=40px style="text-align:center"> Available paths:</h1><br>
    <h2 style="text-align:left">
        <dl>
            <dt>/api/v1.0/precipitation</dt><br>
                <dd>- This retrieves the last 12 months of precipitation data<dd><br>
            <dt>/api/v1.0/stations</dt><br>
                <dd>- Returns a JSON list of stations from the dataset.</dd><br>
            <dt>/api/v1.0/tobs</dt><br>
            <dd>- Returns a JSON list of the dates and temperature observations (TOBS) of the most active station for the last year of data.</dd><br>
            <dt>/api/v1.0/{{start}}</dt><br>
                <dd>- When given the start only, we calculate the Minimum Temperature, Average Temperature, and Maximum Temperature for all dates greater than and equal to the start date.</dd><br>
                <dd>- NOTE:Date range of the data: between: {beginning_date} and: {final_date} </dd><br>
            <dt>/api/v1.0/{{start}}/{{end}}</dt><br>
                <dd>- When given the start and the end date, we calculate the Minimum Temperature, Averure, and Maximum Temperature for all dates greater than and equal to the start date.</dd><br>
                 <dd>- NOTE:Date range of the data: between: {beginning_date} and: {final_date} </dd><br>
        </dl>
    </h2>
    """
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results=session.query(Measurement.date,func.sum(Measurement.prcp)).filter(Measurement.date>='2016-08-23').group_by(Measurement.date).order_by(Measurement.date.asc()).all()
    session.close()
    final_results=[]
    for date, prcp in results:
        final_results.append({
            "Date": date,
            "Precipitation Level (inches)": round(prcp,2)
        })
    return jsonify(final_results)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results=session.query(Station.id,Station.station,Station.name).all()
    session.close()
    final_results=[]
    for id, station, name in results:
        final_results.append({
            "ID": id,
            "Station": station,
            "Name": name
        })
    return jsonify(final_results)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results=session.query(Measurement.date,Measurement.tobs).filter(Measurement.date>='2016-08-23').filter(Measurement.station=='USC00519281').order_by(Measurement.date.asc()).all()
    session.close()
    final_results=[]
    for date, tobs in results:
        final_results.append({
            "Date": date,
            "Temperature Observation Data (TOBS)": tobs
        })
    return jsonify(final_results)

@app.route("/api/v1.0/<start>")
def temperature(start):
    start = dt.datetime.strptime(start, '%Y-%m-%d')
    station_studied='USC00519281'
    session = Session(engine)

    date=session.query(Measurement.date).group_by(Measurement.date).all()
    date_list=list(np.ravel(date))

    for x in date_list:
        if x==start:
            x=start

    temperatures=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date>=start).filter(Measurement.station==station_studied).all()
    session.close()

    results={
            "Minimum Temperature":temperatures[0][0],
            "Average Temperature":round(temperatures[0][1],2),
            "Maximum Temperature":temperatures[0][2]
        }
    return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def temperature_in_time(start,end):
    start = dt.datetime.strptime(start, '%Y-%m-%d')
    end = dt.datetime.strptime(end, '%Y-%m-%d')
    station_studied='USC00519281'
    session = Session(engine)

    date=session.query(Measurement.date).group_by(Measurement.date).all()
    date_list=list(np.ravel(date))

    for x in date_list:
        if x==start:
            x=start

    temperatures=session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(and_(Measurement.date>=start,Measurement.date<=end)).filter(Measurement.station==station_studied).all()
    session.close()

    results={
            "Minimum Temperature":temperatures[0][0],
            "Average Temperature":round(temperatures[0][1],2),
            "Maximum Temperature":temperatures[0][2]
        }
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)