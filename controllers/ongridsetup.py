import pandas as pd
import numpy as np

from controllers.battery import Battery
from controllers.electricity_bill import ElectricityBill
from controllers.inverter import Inverter
from controllers.loads import Loads
from controllers.panels import Panels
from controllers.pvsystem import PvSystem


class OnGridSetup:
    def __init__(self, pvsystem: PvSystem, bill: ElectricityBill, loads: Loads, inverter_controller_type='mppt',
                 info_path='./Components/components_ongrid.xlsx'):
        self.df_setup = pd.DataFrame(columns=['param', 'value'])
        df_inverter = pd.read_excel(info_path, sheet_name='inverter')
        df_panels = pd.read_excel(info_path, sheet_name='panels')
        df_system = pd.read_excel(info_path, sheet_name='system')
        df_battery = pd.read_excel(info_path, sheet_name='battery')

        self.df_load_desired = self._daily_active_energy_demand(bill, df_inverter, df_battery)
        self.df_setup = self.df_setup.append(self._calculate_minimum_needed_power(df_system, pvsystem),
                                             ignore_index=True)

        self.panels = Panels(df_panels, df_system, self.df_setup, controller_type=inverter_controller_type)
        self.battery = Battery(df_battery, self.df_load_desired, df_system, pvsystem)
        self.inverter = Inverter(df_inverter)