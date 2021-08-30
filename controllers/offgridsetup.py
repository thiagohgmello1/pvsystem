import numpy as np
import pandas as pd

from controllers.battery import Battery
from controllers.controller import Controller
from controllers.inverter import Inverter
from controllers.panels import Panels
from controllers.pvsystem import PvSystem
from controllers.electricity_bill import ElectricityBill
from controllers.loads import Loads


class OffGridSetup:
    def __init__(self, pvsystem: PvSystem, bill: ElectricityBill, loads: Loads, controller_type='mppt',
                 info_path='./Components/components_offgrid.xlsx'):
        self.df_setup = pd.DataFrame(columns=['param', 'value'])
        df_inverter = pd.read_excel(info_path, sheet_name='inverter')
        df_panels = pd.read_excel(info_path, sheet_name='panels')
        df_system = pd.read_excel(info_path, sheet_name='system')
        df_battery = pd.read_excel(info_path, sheet_name='battery')
        df_controller = pd.read_excel(info_path, sheet_name='controller')

        self.df_load_desired = self._daily_active_energy_demand(bill, df_inverter, df_battery)
        self.df_setup = self.df_setup.append(self._calculate_minimum_needed_power(df_system, pvsystem),
                                             ignore_index=True)

        self.panels = Panels(df_panels, df_system, self.df_setup, df_controller, controller_type)
        self.controller = Controller(df_controller, self.panels)
        self.battery = Battery(df_battery, self.df_load_desired, df_system, pvsystem)
        self.inverter = Inverter(df_inverter)


    def _calculate_minimum_needed_power(self, df_system, pv: PvSystem):
        red1 = df_system.loc[df_system['param'] == 'red1'].values[0][1]
        red2 = df_system.loc[df_system['param'] == 'red2'].values[0][1]

        liquid_irrad = pv.df_liquid_irradiation
        months = [month.month for month in self.df_load_desired.month_year]
        hsp = np.array([liquid_irrad.liquid_irrad.loc[liquid_irrad.month == month].values[0] for month in months])
        minimum_installed_power = max(self.df_load_desired.load_desired / (hsp * red1 * red2))
        return {'param': 'p_min', 'value': minimum_installed_power}


    @staticmethod
    def _daily_active_energy_demand(bill, df_inverter, df_battery, loads=None):
        load_ca = bill.df_bill.daily_consumption.to_numpy()
        load_cc = np.zeros((1, 12))

        battery_eff = df_battery.loc[df_battery['param'] == 'eff'].values[0][1] / 100
        inv_eff = df_inverter.loc[df_inverter['param'] == 'eff'].values[0][1] / 100
        load_desired = load_cc / battery_eff + load_ca / (battery_eff * inv_eff)
        df_load_desired = pd.DataFrame()
        df_load_desired['month_year'] = bill.df_bill.month_year
        df_load_desired['load_desired'] = pd.Series(load_desired[0])
        return df_load_desired
