import pandas as pd
import pytz
from unidecode import unidecode


class Date:
    def __init__(self, lower_date: str, upper_date: str, freq: str, specific_dates: [str]):
        self.start_date = lower_date
        self.end_date = upper_date
        self.tz = self._timezone()
        self.general_dates = self._general_date_range(freq)
        self.specific_dates = self._to_date_time(specific_dates)

    @staticmethod
    def _timezone():
        time_zones = pytz.all_timezones
        search = unidecode((input('Insert country or Continent to search: ').title()).replace(' ', '_'))
        for tz in time_zones:
            if search in tz:
                result = tz
                break
        else:
            result = 'America/Sao_Paulo'
        return result

    def _general_date_range(self, freq):
        return pd.date_range(self.start_date, self.end_date, closed='left', freq=freq, tz=self.tz)

    @staticmethod
    def _to_date_time(dates: [str]):
        return pd.to_datetime(dates)
