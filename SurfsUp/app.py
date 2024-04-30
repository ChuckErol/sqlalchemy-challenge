# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///SurfsUp/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement  
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    last_twelve = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp)\
                .filter(Measurement.date >= last_twelve).all()
    precipitation_dic = {date: prcp for date, prcp in precipitation}
    session.close()

    return jsonify(precipitation_dic)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station.station).all()
    stations_list = [station[0] for station in stations]
    session.close()

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_active_stations = session.query(Measurement.station,func.count(Measurement.station)
                    ).group_by(Measurement.station
                    ).order_by(func.count(Measurement.station).desc()).all()
    most_active_station_id = most_active_stations[0][0]
    last_twelve = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    tobs = session.query(Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= last_twelve).all()
    temperatures_list = [temp[0] for temp in tobs]
    session.close()

    return jsonify(temperatures_list)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                      .filter(Measurement.date >= start).all()
    session.close()
    TMIN, TAVG, TMAX = results[0] if results else (None, None, None)
    return jsonify(TMIN=TMIN, TAVG=TAVG, TMAX=TMAX)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                      .filter(Measurement.date >= start)\
                      .filter(Measurement.date <= end).all()
    session.close()
    TMIN, TAVG, TMAX = results[0] if results else (None, None, None)
    return jsonify(TMIN=TMIN, TAVG=TAVG, TMAX=TMAX)

if __name__ == '__main__':
    app.run(debug=True)
