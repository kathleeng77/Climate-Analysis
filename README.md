# <p align="center"> Climate Analysis of Stations in Hawaii with SQLAlchemy and Flask</p>


## Part 1: SQLAlchemy Object Relational Mapper


#### Initial Exploration and Analysis in ["climate-analysis" Jupyter Notebook](climate-analysis.ipynb)

```python
# import dependencies
%matplotlib inline
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc

# create engine with data
engine = create_engine("sqlite:///data/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()
```

![classes](images/classes.png)



```python
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
inspector = inspect(engine)
```


#### Precipitation Analysis

```python
# inspect measurement columns
columns = inspector.get_columns('measurement')
for c in columns:
    print(c['name'], c["type"])
```

![measurement-types](images/measurement-types.png)

```python
# calculate last data point in the database
latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
latest_date
```

![latest-date](images/latest-date.png)

```python
# date 1 year ago from latest_date 
year_ago = dt.datetime.strptime(latest_date,"%Y-%m-%d") - dt.timedelta(days=366)
year_ago
```
![year-ago-timestamp](images/year-ago.png)


```python
# retrieve the data and precipitation scores
last_year = session.query(Measurement.date,Measurement.prcp).\
            filter(Measurement.date>=year_ago).all()


# save query results as a Pandas DataFrame and set the index to the date column, sort df by date
prcp_df = pd.DataFrame(last_year, columns=["Date","Precipitation"])
prcp_df["Date"] = pd.to_datetime(prcp_df["Date"], format="%Y-%m-%d")
prcp_df.set_index("Date", inplace=True)
sorted_df = prcp_df.sort_values(by="Date", ascending=True)
```


#### Plotting Precipitation Data

```python
# plotting with pandas is not showing max value when using bar but shows max when using line
sorted_df.plot(title="Precipitation in Hawaii from 2016-2017")
plt.xlabel("Date")
plt.ylabel("Precipitation Score")
plt.xticks([])
plt.legend(loc=9)
plt.savefig("images/prcp-line.png", bbox_inches="tight")

plt.show()
```
![precipitation-line-plot](images/prcp-line.png)



#### Summary Stats

```python
# show summary stats
sorted_df.describe()
```
![summary-statistics](images/summary-stats.png)



#### Station Analysis

```python
# inspect station columns
cols = inspector.get_columns('station')
for c in cols:
    print(c['name'], c["type"])
```
![station-types](images/station-types.png)



```python
names = session.query(Station.station,Station.name).group_by(Station.station).all()
names
```
![query-all-names](images/query-all-names.png)



```python
# find how many stations
stations = session.query(Station.id)
stations.count()
```
![station-count](images/station-count.png)


```python
# query count of each station
active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
                        group_by(Measurement.station).\
                        order_by(func.count(Measurement.station).desc()).all()
active_stations
```

![counts-of-each-station](images/counts-of-each-station.png)



```python
# find most active station for next query
most_active = session.query(Measurement.station, func.count(Measurement.station)).\
                        group_by(Measurement.station).\
                        order_by(func.count(Measurement.station).desc()).first()
most_active
```
![most-active-station](images/most-active-station.png)



```python
# query stats for most active station
most_active_stats = session.query(func.min(Measurement.tobs),
                                  func.max(Measurement.tobs),
                                  func.avg(Measurement.tobs)).\
                                filter(Measurement.station == most_active[0]).all()
most_active_stats
```
![most-active-stats](images/most-active-stats.png)


```python
# station with highest temp observations
highest_temps = session.query(Measurement.station,
                              func.count(Measurement.tobs)).\
                            group_by(Measurement.station).\
                            order_by(func.count(Measurement.station).desc()).first()
highest_temps
```

![station-with-highest-temperatures](images/highest-temp-station.png)



```python
# get the temp stats for the station with the highest temp observations
temps = session.query(Measurement.tobs).filter(Measurement.date >= year_ago).\
                        filter(Measurement.station == highest_temps[0]).all()
temps_df = pd.DataFrame(temps, columns=["Temperature"])
temps_df.head()
```

![temperatures-dataframe](images/temp-df.png)


#### Plotting Temperature Data at Waihee Station
```python
# plot hist
temps_df.plot.hist(bins=12, title="Temperature Observations of WAIHEE Station (USC00519281)")
plt.savefig("images/waihee-temps.png", bbox_inches="tight")

plt.show()
```

![waihee-station-temperature-plot](images/waihee-temps.png)



## Part 2: API Routes with FLASK


#### Analysis with @app.route


Using the analysis in my ["climate-analysis" Jupyter Notebook](climate-analysis.ipynb), I created routes that could be run from the browser using Flask in a [Python file](app.py).

* Note for future:  I want to improve this by allowing the user to input their date into a box that would then take them to the page with the results printed in a more understandable way. As of the latest push, the user must follow instructions to put the dates into the url themselves.

```python
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
def home():
    """List all available api routes."""
    return"""<!DOCTYPE><html><h1>List of all available Honolulu, HI API routes</h1><ul>
    <li>List of precipitation scores from the last year:<a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a></li>
    <li>List of stations:<a href="/api/v1.0/stations">/api/v1.0/stations</a></li>
    <li>List of temp observations from the last year:<a href="/api/v1.0/tobs">/api/v1.0/tobs</a></li>
    <li>List of minimum, maximum, and average temperatures for the date provided (replace &ltstart&gt with a date in 'yyyy-mm-dd' format: <a href="/api/v1.0/<start>">/api/v1.0/<start></a></li>
    <li>List of minimum, maximum, and average temperatures for the dates in range provided (replace &ltstart&gt and &ltend&gt with dates in 'yyyy-mm-dd' format): <a href="/api/v1.0/<start>/<end>">/api/v1.0/<start>/<end></a></li>
    </ul></html>"""

@app.route("/api/v1.0/precipitation")
def precipitation():
    """List of precipitation scores from the last year"""
    # calculate the date 1 year ago from latest date in database
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.datetime.strptime(latest_date[0], "%Y-%m-%d") - dt.timedelta(days=366)
    
    # retrieve precipitation scores and convert to dictionary
    last_year = dict(session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= year_ago).all())
    return jsonify(last_year)

@app.route("/api/v1.0/stations")
def stations(): 
    """List of stations"""
    # retrieve stations and convert to list
    stations =  list(np.ravel(session.query(Measurement.station).group_by(Measurement.station).all()))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs(): 
    """List of temp observations from the last year"""
    # calculate year ago from latest date in database
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.datetime.strptime(latest_date[0], "%Y-%m-%d") - dt.timedelta(days=366)

    # retrieve temp observations and convert to list
    temps = list(session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all())
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
def start(start):
    """List of minimum, maximum, and average temperatures for the date provided"""
    # retrieve temp observations from start date given and convert to list 
    start_date = list(session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all())
    return jsonify(start_date)

@app.route("/api/v1.0/<start>/<end>")
def between(start, end):
    """List of minimum, maximum, and average temperatures for the dates in range provided"""
    # retrieve temp observations from start and end dates given and convert to list
    between_dates = list(session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all())
    return jsonify(between_dates)

if __name__ == '__main__':
    app.run(debug=True)
```


## Part 3: Future Analysis

#### Functions that can be used for future analysis of particular dates for taking a trip

I would like to use the following functions to plot the results instead of printing the results.

```python
# return the tmin, tmax, and tavg of the last years' data
def calc_temps(start_date, end_date):
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

start = str(year_ago)
end = latest_date
print(f"The minimum temperature was {calc_temps(start, end)[0][0]}"
      f", the maximum temperature was {calc_temps(start, end)[0][2]}"
     f", and the average temperature was {calc_temps(start, end)[0][1]}.")
```

![temperature-observations-last-year](images/last-year-tobs.png)



```python
# calculate the daily normals (averages for tmin, tmax, and tavg for all historic data matching a specific month and day
def daily_normals(date):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    return session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) == date).all()
    
print(f"The minimum temperature was {daily_normals('12-31')[0][0]}"
      f", the maximum temperature was {daily_normals('12-31')[0][2]}"
     f", and the average temperature was {daily_normals('12-31')[0][1]}.")
```

![temperature-observations-specific-trip-dates](images/trip-tobs.png)