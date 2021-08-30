import pandas as pd
import numpy as np


class Panels:
    def __init__(self, df_panels, df_system, df_setup, df_controller=None, df_inverter=None, controller_type='mppt'):
        self.df_panels = df_panels
        self.df_panels_setup = pd.DataFrame(columns=['param', 'value'])
        v_pmax_temp = self.v_pmax_temp()
        if df_controller is None:
            self._series_on(df_inverter, v_pmax_temp)
            self._paralel_on(df_inverter)
        else:
            if controller_type == 'conventional':
                self._series_conventional_off(df_system, v_pmax_temp)
                self._paralel_conventional_off(df_system, df_setup)
            else:
                self._series_mppt_off(df_controller, v_pmax_temp)
                self._parallel_mppt_off(df_setup)


    def v_pmax_temp(self):
        v_pmax = self.df_panels.loc[self.df_panels['param'] == 'v_pmax'].value.values[0]
        temp_coef = self.df_panels.loc[self.df_panels['param'] == 'voc_temperature_coef'].value.values[0]

        if 'vmp_tmax' in self.df_panels['param'].values:
            vmp_max_temp = self.df_panels.loc[self.df_panels['param'] == 'vmp_tmax']
        else:
            d_temp = 25 - self.df_panels.loc[self.df_panels['param'] == 't_max'].value.values[0]
            vmp_max_temp = v_pmax - d_temp * temp_coef
        if 'vmp_tmin' in self.df_panels['param'].values:
            vmp_min_temp = self.df_panels.loc[self.df_panels['param'] == 'vmp_tmin'].value.values[0]
        else:
            d_temp = 25 - self.df_panels.loc[self.df_panels['param'] == 't_min'].value.values[0]
            vmp_min_temp = v_pmax - d_temp * temp_coef

        return vmp_min_temp, vmp_max_temp


    def _series_conventional_off(self, df_system, vmax):
        v_sys = df_system.loc[df_system['param'] == 'v_nom'].value.values[0]
        vmp_max_temp = vmax[1]
        serie_qty_dict = {'param': 'series_off', 'value': np.ceil(1.2 * v_sys / vmp_max_temp)}
        self.df_panels_setup = self.df_panels_setup.append(serie_qty_dict, ignore_index=True)


    def _paralel_conventional_off(self, df_system, df_setup):
        p_min = df_setup.loc[df_setup['param'] == 'p_min'].value.values[0] * 1000
        v_sys = df_system.loc[df_system['param'] == 'v_nom'].value.values[0]
        ip_max = self.df_panels.loc[self.df_panels['param'] == 'i_pmax'].value.values[0]
        i_panel = p_min / v_sys
        parallel_qty_dict = {'param': 'parallel_off', 'value': np.ceil(i_panel / ip_max)}
        self.df_panels_setup = self.df_panels_setup.append(parallel_qty_dict, ignore_index=True)


    def _series_mppt_off(self, df_controller, voc_temp):
        v_mppt_min = df_controller.loc[df_controller['param'] == 'v_min'].value.values[0]
        v_mppt_max = df_controller.loc[df_controller['param'] == 'v_max'].value.values[0]
        vmp_min_temp, vmp_max_temp = voc_temp
        series_modules_min = np.ceil(v_mppt_min / vmp_max_temp)
        series_modules_max = np.floor(v_mppt_max / vmp_min_temp)
        serie_qty_dict = {'param': 'series_off', 'value': [series_modules_min, series_modules_max]}
        self.df_panels_setup = self.df_panels_setup.append(serie_qty_dict, ignore_index=True)


    def _parallel_mppt_off(self, df_setup):
        p_min = df_setup.loc[df_setup['param'] == 'p_min'].value.values[0] * 1000
        serie_mppt_min, serie_mppt_max = self.df_panels_setup.loc[self.df_panels_setup['param'] == 'series'].\
            value.values[0]
        p_mod = self.df_panels.loc[self.df_panels['param'] == 'p_max'].value.values[0]
        parallel_modules_min = np.ceil(p_min / (serie_mppt_max * p_mod))
        parallel_modules_max = np.ceil(p_min / (serie_mppt_min * p_mod))
        parallel_qty_dict = {'param': 'parallel_off', 'value': [parallel_modules_min, parallel_modules_max]}
        self.df_panels_setup = self.df_panels_setup.append(parallel_qty_dict, ignore_index=True)


    def _series_on(self, df_inverter, v_pmax):
        v_inv_min = df_inverter.loc[df_inverter['param'] == 'v_min'].value.values[0]
        v_inv_max = df_inverter.loc[df_inverter['param'] == 'v_max'].value.values[0]
        vmp_min_temp, vmp_max_temp = v_pmax
        series_modules_min = np.ceil(v_inv_min / vmp_max_temp)
        series_modules_max = np.floor(v_inv_max / vmp_min_temp)
        serie_qty_dict = {'param': 'series_on', 'value': [series_modules_min, series_modules_max]}
        self.df_panels_setup = self.df_panels_setup.append(serie_qty_dict, ignore_index=True)


    def _paralel_on(self, df_inverter):
        i_sc = self.df_panels.loc[self.df_panels['param'] == 'i_sc'].value.values[0]
        ii_max = df_inverter.loc[df_inverter['param'] == 'ii_max'].value.values[0]
        parallel_qty_dict = {'param': 'parallel_off', 'value': np.floor(i_sc / ii_max)}
        self.df_panels_setup = self.df_panels_setup.append(parallel_qty_dict, ignore_index=True)


if __name__ == '__main__':
    path = './Components/components.xlsx'
    df_sys = pd.read_excel(path, sheet_name='system')
    setup = {'param': ['p_min'], 'value': [3.155611]}
    df_set = pd.DataFrame.from_dict(setup)
    df_c = pd.read_excel(path, sheet_name='controller')
    df_p = pd.read_excel(path, sheet_name='panels')
    panels = Panels(df_p, df_sys, df_set, df_c, controller_type='conventional')
    print('oi')
