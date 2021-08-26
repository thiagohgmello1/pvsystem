import pandas as pd
import numpy as np

from controllers.pvsystem import PvSystem


class Battery:
    def __init__(self, df_battery, df_load_desired, df_system, pvsystem: PvSystem):
        self.df_battery = df_battery
        self.df_battery_setup = pd.DataFrame(columns=['param', 'value'])
        if df_battery.loc[df_battery['param'] == 'desired_autonomy'].value.values.size == 0:
            self._calculate_autonomy(pvsystem)
        else:
            self.df_battery_setup = self.df_battery_setup.append(
                {'param': 'desired_autonomy', 'value': df_battery.loc[df_battery['param'] == 'desired_autonomy'].
                    value.values[0]}, ignore_index=True)
        self._parallel_batteries(df_load_desired)
        self._series_batteries(df_system.loc[df_system['param'] == 'v_nom'].value.values[0])


    def _calculate_autonomy(self, pvsystem: PvSystem):
        calculated_autonomy = np.ceil(-0.48 * pvsystem.df_liquid_irradiation.min(axis=0).values[0] / 1000 + 4.58)
        calculated_autonomy_dict = {'param': 'desired_autonomy', 'value': calculated_autonomy}
        self.df_battery = self.df_battery.append(calculated_autonomy_dict, ignore_index=True)


    def _parallel_batteries(self, df_load_desired):
        max_load = df_load_desired['load_desired'].max()
        desired_autonomy = self.df_battery.loc[self.df_battery['param'] == 'desired_autonomy'].value.values[0]
        discharge_depth = self.df_battery.loc[self.df_battery['param'] == 'discharge_depth_pd'].value.values[0]
        cb_20_sys = max_load * desired_autonomy / discharge_depth
        cb_20_bat = self.df_battery.loc[self.df_battery['param'] == 'p_nom_25_ah'].value.values[0]
        parallel_bat_groups = np.ceil(cb_20_sys / cb_20_bat)
        parallel_dict = {'param': 'parallel_bat_groups', 'value': parallel_bat_groups}
        self.df_battery_setup = self.df_battery_setup.append(parallel_dict, ignore_index=True)


    def _series_batteries(self, v_sys):
        v_bat = self.df_battery.loc[self.df_battery['param'] == 'v_nom'].value.values[0]
        series_bat = np.ceil(v_sys / v_bat)
        series_dict = {'param': 'series_bat', 'value': series_bat}
        self.df_battery_setup = self.df_battery_setup.append(series_dict, ignore_index=True)
