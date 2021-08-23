from pvlib import solarposition
from controllers.date import Date


class Location:
    def __init__(self, lat, lon, dates: Date):
        self.lat = lat
        self.lon = lon
        self.solar_pos = self.solar_pos(dates.general_dates)

    def solar_pos(self, dates):
        solar_pos = solarposition.get_solarposition(dates, self.lat, self.lon)
        # Remove nighttime
        solar_pos = solar_pos.loc[solar_pos['apparent_elevation'] > 0, :]
        return solar_pos


if __name__ == '__main__':
    specific_dates = ['2021-03-21', '2021-06-21', '2021-12-21']
    date = Date('2021-01-01 00:00:00', '2022-01-01', '5min', specific_dates)
    location = Location(-19.983223, -44.030741, date)
    print('Finish')
