import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from pvlib import solarposition, irradiance
from pvlib import location as loc
from location import Location
from shading import Shading
from date import Date


class PvSystem:
    def __init__(self, date: Date, location: Location, shading: Shading, irrad_path='data_base/data_base.xlsx'):
        self.date = date
        self.location = location
        self.solar_pos = location.solar_pos
        self.time_delta = pd.Timedelta('24h')
        self.shading = shading.shading
        self.irradiation = self.get_irradiance1(irrad_path)

    def plot_cartesian_chart_with_shading1(self, freq):
        fig, ax = plt.subplots()
        points = ax.scatter(self.solar_pos.azimuth, self.solar_pos.apparent_elevation, s=2,
                            c=self.solar_pos.index.dayofyear, label=None)
        ax.plot(self.shading[:, 0], self.shading[:, 1])
        fig.colorbar(points)

        for hour in np.unique(self.solar_pos.index.hour):
            # choose label position by the largest elevation for each hour
            subset = self.solar_pos.loc[self.solar_pos.index.hour == hour, :]
            height = subset.apparent_elevation
            pos = self.solar_pos.loc[height.idxmax(), :]
            ax.text(pos['azimuth'], pos['apparent_elevation'], str(hour))

        for date in self.date.specific_dates:
            times = pd.date_range(date, date + self.time_delta, freq=freq, tz=self.date.tz)
            sol_pos = solarposition.get_solarposition(times, self.location.lat, self.location.lon)
            sol_pos = sol_pos.loc[sol_pos['apparent_elevation'] > 0, :]
            label = date.strftime('%Y-%m-%d')
            ax.plot(sol_pos.azimuth, sol_pos.apparent_elevation, label=label)

        ax.figure.legend(loc='upper left')
        ax.set_xlabel('Solar Azimuth (degrees)')
        ax.set_ylabel('Solar Elevation (degrees)')
        plt.ylim(0, None)
        plt.show()

    def plot_cartesian_chart_with_shading2(self, freq):
        fig, ax = plt.subplots()
        self.solar_pos = self._data_preprocessing(self.solar_pos)

        shading = self.shading
        shading[:, 0] = -shading[:, 0]
        shading[:, 0] = np.where(shading[:, 0] < -180, shading[:, 0] + 360, shading[:, 0])
        shading = shading[shading[:, 0].argsort()]

        points = ax.scatter(self.solar_pos.azimuth, self.solar_pos.apparent_elevation, s=2,
                            c=self.solar_pos.index.dayofyear, label=None)
        ax.plot(shading[:, 0], shading[:, 1])
        fig.colorbar(points)

        for hour in np.unique(self.solar_pos.index.hour):
            # choose label position by the largest elevation for each hour
            subset = self.solar_pos.loc[self.solar_pos.index.hour == hour, :]
            height = subset.apparent_elevation
            pos = self.solar_pos.loc[height.idxmax(), :]
            ax.text(pos['azimuth'], pos['apparent_elevation'], str(hour))

        for date in self.date.specific_dates:
            times = pd.date_range(date, date + self.time_delta, freq=freq, tz=self.date.tz)
            sol_pos = solarposition.get_solarposition(times, self.location.lat, self.location.lon)
            sol_pos = sol_pos.loc[sol_pos['apparent_elevation'] > 0, :]
            label = date.strftime('%Y-%m-%d')
            sol_pos = self._data_preprocessing(sol_pos)
            ax.plot(sol_pos.azimuth, sol_pos.apparent_elevation, label=label)

        ax.figure.legend(loc='upper left')
        ax.set_xlabel('Solar Azimuth (degrees)')
        ax.set_ylabel('Solar Elevation (degrees)')
        plt.ylim(0, None)
        plt.xlim(180, -180)
        plt.show()

    def plot_polar_chart_with_shading(self, freq):
        ax = plt.subplot(1, 1, 1, projection='polar')
        self.solar_pos = self._data_preprocessing(self.solar_pos)

        # Draw the analemma loops
        points = ax.scatter(np.radians(self.solar_pos.azimuth), self.solar_pos.apparent_zenith,
                            s=2, label=None, c=self.solar_pos.index.dayofyear)
        ax.figure.colorbar(points)

        # Draw hour labels
        for hour in np.unique(self.solar_pos.index.hour):
            # choose label position by the smallest radius for each hour
            subset = self.solar_pos.loc[self.solar_pos.index.hour == hour, :]
            r = subset.apparent_zenith
            pos = self.solar_pos.loc[r.idxmin(), :]
            ax.text(np.radians(pos['azimuth']), pos['apparent_zenith'], str(hour))

        # Draw individual days
        for date in self.date.specific_dates:
            times = pd.date_range(date, date + self.time_delta, freq=freq, tz=self.date.tz)
            sol_pos = solarposition.get_solarposition(times, self.location.lat, self.location.lon)
            sol_pos = sol_pos.loc[sol_pos['apparent_elevation'] > 0, :]
            label = date.strftime('%Y-%m-%d')
            sol_pos = self._data_preprocessing(sol_pos)
            ax.plot(sol_pos.azimuth, sol_pos.apparent_zenith, label=label)

        ax.figure.legend(loc='upper left')

        # Change coordinates to be like a compass
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_rmax(90)
        plt.show()

    @staticmethod
    def get_irradiance1(irrad_path):
        df_irrad = pd.read_excel(irrad_path)
        max_irrad = df_irrad.Irrad_med.max()
        tol = 2
        step_left = df_irrad.index[df_irrad.Irrad_med == max_irrad].tolist()[0]
        step_right = step_left

        while ((step_left - 1) != 0) and ((step_right + 1) != df_irrad.shape[0]):
            d_left = np.abs(df_irrad.Irrad_med.iloc[step_left - 1] - df_irrad.Irrad_med.iloc[step_left])
            d_right = np.abs(df_irrad.Irrad_med.iloc[step_right] - df_irrad.Irrad_med.iloc[step_right + 1])
            if d_left > d_right + tol:
                df_irrad.Irrad_med.iloc[step_left - 1] = df_irrad.Irrad_med.iloc[step_right + 1]
                df_irrad.Irrad_med.iloc[step_left] = df_irrad.Irrad_med.iloc[step_right]
            elif d_right > d_left + tol:
                df_irrad.Irrad_med.iloc[step_right + 1] = df_irrad.Irrad_med.iloc[step_left - 1]
                df_irrad.Irrad_med.iloc[step_right] = df_irrad.Irrad_med.iloc[step_left]
            step_left -= 1
            step_right += 1

        df_norm_irrad = df_irrad[['Date', 'Time', 'Irrad_med']]
        df_norm_irrad.Irrad_med = df_norm_irrad.Irrad_med.apply(lambda x: x / max_irrad)
        fig, ax = plt.subplots()
        ax.plot(df_norm_irrad.Irrad_med)
        plt.show()
        return df_norm_irrad

    def get_irradiance2(self, tilt, surface_azimuth, freq, date):
        times = pd.date_range(date, freq=freq, periods=6 * 24, tz=self.date.tz)

        clear_sky = loc.Location(self.location.lat, self.location.lon, self.date.tz).get_clearsky(times)
        # Get solar azimuth and zenith to pass to the transposition function
        solar_position = solarposition.get_solarposition(times=times)
        # Use the get_total_irradiance function to transpose the GHI to POA
        poa_irradiance = irradiance.get_total_irradiance(
            surface_tilt=tilt,
            surface_azimuth=surface_azimuth,
            dni=clear_sky['dni'],
            ghi=clear_sky['ghi'],
            dhi=clear_sky['dhi'],
            solar_zenith=solar_position['apparent_zenith'],
            solar_azimuth=solar_position['azimuth'])
        # Return DataFrame with only GHI and POA
        return pd.DataFrame({'GHI': clear_sky['ghi'],
                             'POA': poa_irradiance['poa_global']})

    @staticmethod
    def _data_preprocessing(solar_pos):
        solar_pos['azimuth'] = -solar_pos['azimuth']
        solar_pos['azimuth'].loc[solar_pos['azimuth'] <= -180] = solar_pos['azimuth'] + 360
        return solar_pos
