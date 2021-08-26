import pandas as pd
import numpy as np


class Panels:
    def __init__(self, df_panels, df_system, df_setup, df_controller):
        self.df_panels = df_panels
        self.df_panels_setup = pd.DataFrame(columns=['param', 'value'])
        vmax = self._vmax_temp()
        self._series_conventional(df_system, vmax)
        self._paralel_conventional(df_system, df_setup)
        self._series_mppt(df_controller, vmax)
        self._parallel_mppt(df_setup)


    def _vmax_temp(self):
        v_oc = self.df_panels.loc[self.df_panels['param'] == 'v_oc'].value.values[0]
        temp_coef = self.df_panels.loc[self.df_panels['param'] == 'voc_temperature_coef'].value.values[0]

        if 'vmp_tmax' in self.df_panels['param']:
            vmp_max_temp = self.df_panels.loc[self.df_panels['param'] == 'vmp_tmax']
        else:
            d_temp = 25 - self.df_panels.loc[self.df_panels['param'] == 't_max'].value.values[0]
            vmp_max_temp = v_oc + d_temp * temp_coef
        if 'vmp_tmin' in self.df_panels['param']:
            vmp_min_temp = self.df_panels.loc[self.df_panels['param'] == 'vmp_tmin'].value.values[0]
        else:
            d_temp = 25 - self.df_panels.loc[self.df_panels['param'] == 't_min'].value.values[0]
            vmp_min_temp = v_oc + d_temp * temp_coef

        return vmp_min_temp, vmp_max_temp


    def _series_conventional(self, df_system, vmax):
        v_sys = df_system.loc[df_system['param'] == 'v_nom'].value.values[0]
        vmp_max_temp = vmax[1]
        serie_qty_dict = {'param': 'conventional_series', 'value': np.ceil(1.2 * v_sys / vmp_max_temp)}
        self.df_panels_setup = self.df_panels_setup.append(serie_qty_dict, ignore_index=True)


    def _paralel_conventional(self, df_system, df_setup):
        p_min = df_setup.loc[df_setup['param'] == 'p_min'].value.values[0] * 1000
        v_sys = df_system.loc[df_system['param'] == 'v_nom'].value.values[0]
        ip_max = self.df_panels.loc[self.df_panels['param'] == 'i_pmax'].value.values[0]
        i_panel = p_min / v_sys
        parallel_qty_dict = {'param': 'conventional_parallel', 'value': np.ceil(i_panel / ip_max)}
        self.df_panels_setup = self.df_panels_setup.append(parallel_qty_dict, ignore_index=True)


    def _series_mppt(self, df_controller, vmax):
        v_mppt_min = df_controller.loc[df_controller['param'] == 'v_min'].value.values[0]
        v_mppt_max = df_controller.loc[df_controller['param'] == 'v_max'].value.values[0]
        vmp_min_temp, vmp_max_temp = vmax
        series_modules_min = np.ceil(v_mppt_min / vmp_max_temp)
        series_modules_max = np.ceil(v_mppt_max / vmp_min_temp)
        serie_qty_dict = {'param': 'mppt_serie', 'value': [series_modules_min, series_modules_max]}
        self.df_panels_setup = self.df_panels_setup.append(serie_qty_dict, ignore_index=True)


    def _parallel_mppt(self, df_setup):
        p_min = df_setup.loc[df_setup['param'] == 'p_min'].value.values[0] * 1000
        serie_mppt_min, serie_mppt_max = self.df_panels_setup.loc[self.df_panels_setup['param'] == 'mppt_serie'].\
            value.values[0]
        p_mod = self.df_panels.loc[self.df_panels['param'] == 'p_max'].value.values[0]
        parallel_modules_min = np.ceil(p_min / (serie_mppt_max * p_mod))
        parallel_modules_max = np.ceil(p_min / (serie_mppt_min * p_mod))
        parallel_qty_dict = {'param': 'mppt_parallel', 'value': [parallel_modules_min, parallel_modules_max]}
        self.df_panels_setup = self.df_panels_setup.append(parallel_qty_dict, ignore_index=True)


if __name__ == '__main__':
    path = './Components/components.xlsx'
    df_sys = pd.read_excel(path, sheet_name='system')
    setup = {'param': ['p_min'], 'value': [3.155611]}
    df_set = pd.DataFrame.from_dict(setup)
    df_c = pd.read_excel(path, sheet_name='controller')
    controller = Panels(path, df_sys, df_set, df_c)
