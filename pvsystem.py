import pandas as pd
import numpy as np
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
        self.shading = shading.shading
        self.solar_pos = self._calculate_shading_influence(self.solar_pos)
        self.irradiation = self.get_irradiance1(irrad_path)
        self.utilization_factor()


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

        # Draw specific dates
        for date in self.date.specific_dates:
            time_delta = pd.Timedelta('24h')
            times = pd.date_range(date, date + time_delta, freq=freq, tz=self.date.tz)
            df_solar_pos = solarposition.get_solarposition(times, self.location.lat, self.location.lon)
            df_solar_pos = df_solar_pos.loc[df_solar_pos['apparent_elevation'] > 0, :]
            label = date.strftime('%Y-%m-%d')
            ax.plot(df_solar_pos.azimuth, df_solar_pos.apparent_elevation, label=label)

        ax.figure.legend(loc='upper left')
        ax.set_xlabel('Solar Azimuth (degrees)')
        ax.set_ylabel('Solar Elevation (degrees)')
        plt.ylim(0, None)
        plt.savefig('outputs/pvsystem/c_chart_shading1.png', dpi=80)
        # plt.show()


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

        # Draw specific dates
        for date in self.date.specific_dates:
            time_delta = pd.Timedelta('24h')
            times = pd.date_range(date, date + time_delta, freq=freq, tz=self.date.tz)
            df_solar_pos = solarposition.get_solarposition(times, self.location.lat, self.location.lon)
            df_solar_pos = df_solar_pos.loc[df_solar_pos['apparent_elevation'] > 0, :]
            label = date.strftime('%Y-%m-%d')
            df_solar_pos = self._data_preprocessing(df_solar_pos)
            ax.plot(df_solar_pos.azimuth, df_solar_pos.apparent_elevation, label=label)

        ax.figure.legend(loc='upper left')
        ax.set_xlabel('Solar Azimuth (degrees)')
        ax.set_ylabel('Solar Elevation (degrees)')
        plt.ylim(0, None)
        plt.xlim(180, -180)
        plt.savefig('outputs/pvsystem/c_chart_shading2.png', dpi=80)
        # plt.show()


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
            time_delta = pd.Timedelta('24h')
            times = pd.date_range(date, date + time_delta, freq=freq, tz=self.date.tz)
            df_solar_pos = solarposition.get_solarposition(times, self.location.lat, self.location.lon)
            df_solar_pos = df_solar_pos.loc[df_solar_pos['apparent_elevation'] > 0, :]
            label = date.strftime('%Y-%m-%d')
            df_solar_pos = self._data_preprocessing(df_solar_pos)
            ax.plot(df_solar_pos.azimuth, df_solar_pos.apparent_zenith, label=label)

        ax.figure.legend(loc='upper left')

        # Change coordinates to be like a compass
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_rmax(90)
        plt.savefig('outputs/pvsystem/p_chart_shading.png', dpi=80)
        # plt.show()


    def _plot_cartesian_chart_shading_losses(self, df_solar_pos):
        fig, ax = plt.subplots()
        ax.scatter(df_solar_pos.azimuth, df_solar_pos.shading, s=2, c=df_solar_pos.index.dayofyear, label=None)
        ax.plot(self.shading[:, 0], self.shading[:, 1])


    # TODO Fix warning
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
        plt.savefig('outputs/pvsystem/experimental_irrad.png', dpi=80)
        # plt.show()

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


    def _calculate_shading_influence(self, df_solar_pos):
        b = pd.DataFrame(self.shading)[0]

        d_azimuth = abs(self.shading[1][0] - self.shading[0][0])
        round_digit = round(d_azimuth, int(np.ceil(-np.log10(d_azimuth))))
        tol = round_digit + 10 ** (np.floor(np.log10(d_azimuth)))

        azimuth = df_solar_pos['azimuth'].apply(np.isclose, b=b, atol=tol)
        df_solar_pos['closest_shading'] = [self.shading[np.argwhere(serie == True)[0][0]][1] for serie in azimuth]
        df_solar_pos['shading'] = np.where(df_solar_pos.apparent_elevation < df_solar_pos.closest_shading, 0,
                                           df_solar_pos.apparent_elevation)
        return df_solar_pos


    def adjust_irradiance(self, df_solar_pos, plot=False):
        num_points = self.irradiation.shape[0]
        start = pd.Timestamp(df_solar_pos.index[0].strftime('%X'))
        end = pd.Timestamp(df_solar_pos.index[-1].strftime('%X'))
        sun_period = pd.DataFrame()
        sun_period['time'] = pd.to_datetime(np.linspace(start=start.value, stop=end.value, num=num_points))
        sun_period['x_axis'] = pd.to_datetime(np.linspace(start=start.value, stop=end.value, num=num_points))\
            .strftime("%H:%M:%S")
        sun_period['y_axis'] = self.irradiation.Irrad_med

        if plot:
            sun_period.plot(x='x_axis', y='y_axis', xlabel='Time', ylabel='Irradiance (pu)', legend=False)
            plt.gcf().autofmt_xdate()

        return sun_period


    def utilization_factor(self, date='2021-08-20', freq='5min'):
        df_solar_pos = self.generate_solar_position(date, freq)
        df_sun_period = self.adjust_irradiance(df_solar_pos)
        tol = pd.Timedelta(freq)
        b = pd.DataFrame([pd.Timestamp(idx.strftime('%H:%M:%S')) for idx in df_solar_pos.index])
        time = df_sun_period['x_axis'].apply(np.isclose, b=b, atol=tol)


    def generate_solar_position(self, date='2021-08-20', freq='5min'):
        time_delta = pd.Timedelta('24h')
        date = pd.to_datetime(date)
        times = pd.date_range(date, date + time_delta, freq=freq, tz=self.date.tz)
        df_solar_pos = solarposition.get_solarposition(times, self.location.lat, self.location.lon)
        df_solar_pos = df_solar_pos.loc[df_solar_pos['apparent_elevation'] > 0, :]
        return df_solar_pos


    @staticmethod
    def _data_preprocessing(solar_pos):
        solar_pos['azimuth'] = -solar_pos['azimuth']
        solar_pos['azimuth'].loc[solar_pos['azimuth'] <= -180] = solar_pos['azimuth'] + 360
        return solar_pos
