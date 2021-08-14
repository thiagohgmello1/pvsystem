from pvlib import solarposition
from date import Date


class Location:
    def __init__(self, lat, lon, dates: Date):
        self.lat = lat
        self.lon = lon
        self.solar_pos = self.solar_pos(dates.general_dates)
        # self.specific_sun_pos = self.solar_pos(dates.specific_dates)

    def solar_pos(self, dates):
        solar_pos = solarposition.get_solarposition(dates, self.lat, self.lon)
        # Remove nighttime
        solar_pos = solar_pos.loc[solar_pos['apparent_elevation'] > 0, :]
        return solar_pos
