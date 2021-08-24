import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class Loads:
    def __init__(self, file='./Bills/test_file.xlsx', winter_coef=20):
        self.df_ca_loads = pd.read_excel(file, sheet_name='ca_loads', dtype={'hours_used': float, 'qty': np.int8})
        self.df_cc_loads = pd.read_excel(file, sheet_name='cc_loads', dtype={'hours_used': float, 'qty': np.int8})
        self.df_ca_load_period = pd.read_excel(file, sheet_name='ca_load_period')
        self.df_cc_load_period = pd.read_excel(file, sheet_name='cc_load_period')
        self.df_ca_load_curve = self._calculate_load_curve(self.df_ca_loads, self.df_ca_load_period)
        self.df_cc_load_curve = self._calculate_load_curve(self.df_cc_loads, self.df_cc_load_period)

    @staticmethod
    def _calculate_load_curve(df_load, df_period):
        df_load_curve = pd.DataFrame(columns=df_period.columns)
        for i, row in df_period.iterrows():
            x_sum = df_period.iloc[i].count() - 1
            power = df_load.iloc[i]['power_nominal'] * df_load.iloc[i]['qty'] * df_load.iloc[i]['hours_used'] / x_sum
            m = row != 'x'
            df_load_curve = df_load_curve.append(row.where(m, power))
        df_load_curve.fillna(0, inplace=True)
        return df_load_curve

    @staticmethod
    def plot_load_curve(df_load_curve, output_f='outputs/loads/load_curve.png'):
        if df_load_curve.empty:
            print(f'No load to plot.')
        else:
            s = df_load_curve.sum(numeric_only=True, skipna=True)
            s.plot()
            plt.xlabel('Hora')
            plt.ylabel('Potência (W)')
            plt.ylim((0, None))
            plt.title('Curva de Carga')
            plt.savefig(output_f, dpi=80)
            plt.show()


if __name__ == '__main__':
    loads = Loads()
    loads.plot_load_curve(loads.df_ca_load_curve)
    loads.plot_load_curve(loads.df_cc_load_curve)
