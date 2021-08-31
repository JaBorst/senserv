import pathlib
from datetime import datetime
import time
import sqlite3
import multiprocessing
import pandas as pd

class SensorWrapper():
    def __init__(self, sensor, measure:list):
        self.sensor=sensor
        self.measure=measure
    def get(self):
        return {k:self.sensor.__dict__[k]  for k in self.measure}

class TestSensor:
    def __init__(self):
        self.temperature = 40
        self.pressure = 1000
class TestSensor2:
    def __init__(self):
        self.temperature = 20
        self.humidity = 234



class AHT():
    def __init__(self, s):
        self.s = s
        self.measure = ["temperature", "relative_humidity"]

    def get(self):
        return {
            "temperature": self.s.temperature,
            "relative_humidity": self.s.relative_humidity
        }

class BMP():
    def __init__(self,s):
        self.s = s
        self.measure =  ["pressure", "altitude", "temperature"]
    def get(self):
        return{
            "pressure": self.s.pressure,
            "altitude": self.s.altitude,
            # "temperature":self.s.temperature
        }

def timestamp():
    return datetime.now().isoformat()

class Store():
    def __init__(self, keys, db=None, location=None):
        print("input location", location)
        self._keys = keys
        if db is None:
            self.db=pathlib.Path("senserv_db.sqlite")
        else:
            self.db = pathlib.Path(db)

        self.location = location
        if not (location is None):
            if location.get() != "":
                self._conditional_create()

    def read(self, what=None, start=None, end=None, pandas=True):
        print(what)

        if what is None:
            what = "*"
        else:
            what = [what] if isinstance(what, str) else what
            what = ",".join(["timestamp"]+what)
        sql = f"SELECT {what} FROM {self.location.get()}"

        with sqlite3.connect(self.db) as self.connection:
            if pandas:
                r = pd.read_sql_query(sql, self.connection)
            else:
                self.cursor = self.connection.cursor()
                r = self.cursor.execute(sql).fetchall()
        return r

    def _conditional_create(self):
        print("Creating")
        with sqlite3.connect(self.db) as self.connection:
            self.cursor = self.connection.cursor()
            self.cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {self.location.get()} (timestamp text, {','.join([x + ' float' for x in self._keys])});")
            self.connection.commit()

    def write(self,timestamp, data):
        with sqlite3.connect(self.db) as self.connection:
            self.cursor = self.connection.cursor()
            timestamp = f"\"{timestamp}\""
            sql = f"INSERT INTO {self.location.get()} ({','.join(['timestamp'] + self._keys)}) VALUES( {','.join([timestamp] + [str(data[x]) for x in self._keys])});"
            self.cursor.execute(sql)
            print(".")
            self.connection.commit()

    def connection(self):
        return sqlite3.connect(self.db)

    def tables(self):
        with sqlite3.connect(self.db) as self.connection:
            self.cursor = self.connection.cursor()
            r = self.cursor.execute("select name from sqlite_master where type = 'table';").fetchall()
            print(r)
        return r

class SensorList:
    def __init__(self, sensors):
        self.sensors = sensors
        self._keys = sorted(list(set(sum([x.measure for x in self.sensors], []))))
        self._separator = "\t"


    def all(self):
        results = [s.get() for s in self.sensors]
        d = {k:[] for k in self._keys}
        for k in self._keys:
            for r in results:
                if k in r :
                    d[k].append(r[k])
        d = {k: sum(v)/len(v) for k,v in d.items()}
        return d



class SensorsSystem:
    def __init__(self, sl,  interval=60, location=None):
        self.sl = sl if isinstance(sl, SensorList) else SensorList(sl)
        self.store = Store(keys=self.sl._keys, location=location)
        self.interval = interval

    def all(self):
        return self.sl.all()

    def log(self):
        self.store.write(timestamp(), self.sl.all())

    def run(self):
        def _run():
            while True:
                self.log()
                time.sleep(self.interval)

        self.daemonLoop = multiprocessing.Process(name='Daemon', target=_run)
        self.daemonLoop.start()

    def stop(self):
        self.daemonLoop.terminate()

    def read(self, what=None, start=None, end=None):
        self.store.read(what=what, start=start, end=end)

    def change_location(self, location):
        self.stop()
        self.location = location
        self.store = Store(keys=self.sl._keys, location=location)
        self.run()