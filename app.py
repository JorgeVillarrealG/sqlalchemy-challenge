import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
#Data base setup
engine=create_engine("sqlite:///Resources/hawaii.sqlite")

#Prepare Base
Base=automap_base()
Base.prepare(engine,reflect=True)
Measurement=Base.classes.measurement
Station=Base.classes.station
#Flask Setup 
app= Flask(__name__)
#Routes 
@app.route("/")
def home():
    return f"""
    <p> Available Routes:<p>
    <p>/apo/v1.0/precipitation<p>
    <p>/api/v1.0/stations<p>
    <p>/api/v1.0/tobs<p>
    <p>/api/v1.0/<start><p>
    <p>/api/v1.0/<start>/<end><p>
"""
@app.route("/apo/v1.0/precipitation")
def precipitation():
    session=Session(engine)
    results=session.query(Measurement.date,Measurement.prcp).all()
    output=[]
    for date,prcp in results:
        output.append({
            "Date":date,
            "Precipitation":prcp
        })
    return jsonify(output) 
@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    results=session.query(Station.station).all()
    output=[]
    for x in results:
        output.append(x)
    return jsonify(output)
@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
    mactive=session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    date_last=session.query(Measurement.date).filter_by(station=mactive.station).order_by(Measurement.date.desc()).first()
    year,month,day = date_last.date.split("-")
    query_date=dt.date(int(year),int(month),int(day))-dt.timedelta(days=365)
    query=(session.query(Measurement.station,Measurement.date,Measurement.tobs)
    .filter(Measurement.station==mactive.station,Measurement.date>=query_date).all()
    )
    output=[]
    for station,date,tobs in query:
        output.append({
            "Station":station,
            "Date":date,
            "TOBS":tobs
        })
    return jsonify(output)
@app.route("/api/v1.0/<start>")
def temp(start):
    session=Session(engine)
    max= session.query(Measurement.tobs).filter(Measurement.date>=start).order_by(Measurement.tobs.desc()).first()
    min=session.query(Measurement.tobs).filter(Measurement.date>=start).order_by(Measurement.tobs).first()
    average=session.query(func.avg(Measurement.tobs)).filter(Measurement.date>=start).all()
    response={
        "Max":max[0],
        "Min":min[0],
        "Average":average[0][0]
    }
    return jsonify(response)

@app.route("/api/v1.0/<start>/<end>")
def tempSE(start,end):
    session=Session(engine)
    max= session.query(Measurement.tobs).filter(Measurement.date>=start,Measurement.date<end).order_by(Measurement.tobs.desc()).first()
    min=session.query(Measurement.tobs).filter(Measurement.date>=start, Measurement.date<end).order_by(Measurement.tobs).first()
    average=session.query(func.avg(Measurement.tobs)).filter(Measurement.date>=start, Measurement.date<end).all()
    response={
        "Max":max[0],
        "Min":min[0],
        "Average":average[0][0]
    }
    return jsonify(response)
        
if __name__=="__main__":
    app.run(debug=True)

