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
        self.calculate_autonomy(pvsystem)
        self.load_desired = self.daily_active_energy_demand(bill, loads)


    def calculate_autonomy(self, pvsytem: PvSystem):
        calculated_autonomy = np.ceil(-0.48 * pvsytem.liquid_irradiation.min(axis=0).values[0] / 1000 + 4.58)
        self.df_battery.append(['calculated_autonomy', calculated_autonomy])


    def daily_active_energy_demand(self, bill, loads):
        if loads is None:
            source = bill.df_bill.daily_consumption
        else:
            source = loads

        battery_eff = self.df_battery.loc[self.df_battery['param'] == 'eff'].values[0][1]
        inv_eff = self.df_inverter.loc[self.df_inverter['param'] == 'eff'].values[0][1]
        load_desired = np.array([])
        return load_desired
