from pathlib import Path
import datetime
import numpy
import pickle


class Generator:
    def __init__(self, network, models_path):
        self._network = network
        if not models_path:
            models_path = Path(__file__).parent

        with open(models_path / 'p.pickle', 'rb') as f:
            self._p = pickle.load(f)
        with open(models_path / 'q.pickle', 'rb') as f:
            self._q = pickle.load(f)

    def generate(self, bus_id, meas_type):

        now = datetime.datetime.now()
        vector = []
        vector.extend(_get_season_vector(now))
        vector.extend(_get_day_vector(now))
        vector.extend(_get_time_vector(now))
        vector.extend(_get_bus_vector(self._network, bus_id))
        vector = numpy.array(vector)
        vector = vector.reshape(1, -1)

        if meas_type == 'p':
            return self._p.predict(vector)[0]
        elif meas_type == 'q':
            return self._q.predict(vector)[0]
        else:
            raise ValueError


def _get_season_vector(now):
    year = 2000
    dummy = now.replace(year=year)
    season = None
    if dummy < datetime.datetime(year, 3, 20):
        season = 'winter'
    elif dummy < datetime.datetime(year, 6, 21):
        season = 'spring'
    elif dummy < datetime.datetime(year, 9, 23):
        season = 'summer'
    elif dummy < datetime.datetime(year, 12, 21):
        season = 'autumn'
    else:
        season = 'winter'
    return (s == season for s in ['spring', 'summer', 'autumn', 'winter'])


def _get_day_vector(now):
    weekday = now.weekday()
    return (weekday < 5, weekday == 5, weekday == 6)


def _get_time_vector(now):
    return (now.hour, now.minute)


def _get_bus_vector(network, bus_id):
    p = (network.load[network.load.bus == bus_id].p_mw.sum()
         - network.sgen[network.sgen.bus == bus_id].p_mw.sum())
    q = (network.load[network.load.bus == bus_id].q_mvar.sum()
         - network.sgen[network.sgen.bus == bus_id].q_mvar.sum())
    return (p, q, network.bus.iloc[bus_id].vn_kv)
