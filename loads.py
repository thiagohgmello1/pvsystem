import pandas as pd


class Loads:
    def __init__(self, file):
        self.df_ca_loads = pd.read_excel(file, sheet_name='ca_loads')
        self.df_cc_loads = pd.read_excel(file, sheet_name='cc_loads')
        self.df_ca_load_period = pd.read_excel(file, sheet_name='ca_load_period')
        self.df_cc_load_period = pd.read_excel(file, sheet_name='cc_load_period')
        self.df_ca_load_curve = self.calculate_load_curve(self.df_ca_loads, self.df_ca_load_period)

    @staticmethod
    def calculate_load_curve(df_load, df_period):

        return 0

