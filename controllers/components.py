import numpy as np
import pandas as pd
from controllers.pvsystem import PvSystem
from controllers.electricity_bill import ElectricityBill
from controllers.loads import Loads


class Components:
    def __init__(self, pvsystem: PvSystem, bill: ElectricityBill, loads: Loads,
                 info_path='./Components/components.xlsx'):
        self.df_battery = pd.read_excel(info_path, sheet_name='battery')
        self.df_inverter = pd.read_excel(info_path, sheet_name='inverter')
        self.df_panels = pd.read_excel(info_path, sheet_name='panels')
        self.df_system = pd.read_excel(info_path, sheet_name='system')
        self.df_controller = pd.read_excel(info_path, sheet_name='controller')
        self.setup = pd.DataFrame()
        self._calculate_autonomy(pvsystem)
        self.df_load_desired = self._daily_active_energy_demand(bill, loads)
        self.minimum_needed_power = self._calculate_minimum_needed_power(pvsystem)


    def _calculate_autonomy(self, pvsytem: PvSystem):
        calculated_autonomy = np.ceil(-0.48 * pvsytem.df_liquid_irradiation.min(axis=0).values[0] / 1000 + 4.58)
        self.df_battery.append(['calculated_autonomy', calculated_autonomy])


    def _daily_active_energy_demand(self, bill, loads):
        load_ca = bill.df_bill.daily_consumption.to_numpy()
        load_cc = np.zeros((1, 12))

        battery_eff = self.df_battery.loc[self.df_battery['param'] == 'eff'].values[0][1] / 100
        inv_eff = self.df_inverter.loc[self.df_inverter['param'] == 'eff'].values[0][1] / 100
        load_desired = load_cc / battery_eff + load_ca / (battery_eff * inv_eff)
        df_load_desired = pd.DataFrame()
        df_load_desired['month_year'] = bill.df_bill.month_year
        df_load_desired['load_desired'] = pd.Series(load_desired[0])
        return df_load_desired


    def _calculate_minimum_needed_power(self, pv: PvSystem):
        red1 = self.df_system.loc[self.df_system['param'] == 'red1'].values[0][1]
        red2 = self.df_system.loc[self.df_system['param'] == 'red2'].values[0][1]

        liquid_irrad = pv.df_liquid_irradiation
        months = [month.month for month in self.df_load_desired.month_year]
        hsp = np.array([liquid_irrad.liquid_irrad.loc[liquid_irrad.month == month].values[0] for month in months])
        minimum_installed_power = max(self.df_load_desired.load_desired / (hsp * red1 * red2))
        return minimum_installed_power


    def conventional_controller_choice(self):
        pass
