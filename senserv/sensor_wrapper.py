import pathlib
from datetime import datetime
import time



class SensorWrapper():
    def __init__(self, sensor, measure:list):
        self.sensor=sensor
        self.measure=measure
    def get(self):
        return {k:self.sensor.__dict__[k]  for k in self.measure}


def timestamp():
    # return datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    return datetime.now().isoformat()

class SensorList:
    def __init__(self, sensors, log=None, interval=10):
        self.sensors = sensors
        self.interval=interval
        self._keys = sorted(list(set(sum([x.measure for x in self.sensors], []))))
        self._separator = "\t"

        log = log if log is not None else f"{timestamp()}_measurement.log"
        self._log_file = log if isinstance(log, pathlib.Path) else pathlib.Path(log)
        if not self._log_file.exists():
            with open(self._log_file, "w") as f:
                f.write(self._separator.join(["timestamp"] + self._keys) +"\n")

    def all(self):
        results = [s.get() for s in self.sensors]
        d = {k:[] for k in self._keys}
        for k in self._keys:
            for r in results:
                if k in r :
                    d[k].append(r[k])
        return d

    def log(self):
        r = self.all()
        with open (self._log_file, "a") as f:
            f.write(self._separator.join([timestamp()] + [str(r[k]) for k in self._keys]) + "\n")
        return r

    def run(self):
        while True:
            print(self.log())
            time.sleep(self.interval)



class TestSensor:
    def __init__(self):
        self.temperature = 40
        self.pressure = 1000
class TestSensor2:
    def __init__(self):
        self.temperature = 20
        self.humidity = 234

test_list_sensors= SensorWrapper(TestSensor(), ["temperature", "pressure"]),  SensorWrapper(TestSensor2(), ["temperature","humidity"])
test_sensors= SensorWrapper(TestSensor(), ["temperature", "pressure"]),  SensorWrapper(TestSensor2(), ["temperature","humidity"])
