import numpy as np
import pandas as pd

from controllers.panels import Panels


class Controller:
    def __init__(self, df_controller, panels: Panels):
        self.df_controller = df_controller
        self.df_controller_setup = pd.DataFrame(columns=['param', 'value'])
        # self._supportability(panels.df_panels, panels.df_panels_setup)
        self._calculate_current_demand(panels)
        self._calculate_parallel_controllers()
        self._check_voltage(panels)


    def _supportability(self, df_panels, df_panels_setup):
        i_pmax = df_panels.loc[df_panels['param'] == 'i_pmax'].value.values[0]
        parallel_controllers = self.df_controller.loc[self.df_controller['param'] == 'parallel_controllers'].value.\
            values[0]
        i_controller = self.df_controller.loc[self.df_controller['param'] == 'i_load'].value.values[0]
        min_parallel, max_parallel = df_panels_setup.loc[df_panels_setup['param'] == 'mppt_parallel'].value.values[0]
        i_total_controller = i_controller * parallel_controllers
        min_supportability = i_total_controller > min_parallel * i_pmax
        max_supportability = i_total_controller > max_parallel * i_pmax
        supportability_dict = {'param': 'supportability', 'value': [min_supportability, max_supportability]}
        self.df_controller_setup = self.df_controller_setup.append(supportability_dict, ignore_index=True)


    def _calculate_current_demand(self, panels: Panels):
        i_sc = panels.df_panels.loc[panels.df_panels['param'] == 'i_sc'].value.values[0]
        parallel_modules = np.array(panels.df_panels_setup.loc[panels.df_panels_setup['param'] == 'parallel'].value.
                                    values[0])
        i_c = (1.25 * parallel_modules * i_sc).tolist()
        min_current_dict = {'param': 'min_current', 'value': i_c}
        self.df_controller_setup = self.df_controller_setup.append(min_current_dict, ignore_index=True)


    def _calculate_parallel_controllers(self):
        i_ctl = self.df_controller.loc[self.df_controller['param'] == 'i_ctl'].value.values[0]
        i_c = np.array(self.df_controller_setup.loc[self.df_controller_setup['param'] == 'min_current'].value.values[0])
        parallel_controllers = np.ceil(i_c / i_ctl).tolist()
        parallel_dict = {'param': 'parallel', 'value': parallel_controllers}
        self.df_controller_setup = self.df_controller_setup.append(parallel_dict, ignore_index=True)


    def _check_voltage(self, panels: Panels):
        v_oc_tmin = panels.v_pmax_temp()[0]
        series = np.array(panels.df_panels_setup.loc[panels.df_panels_setup['param'] == 'series'].value.values[0])
        v_modules = v_oc_tmin * series
        v_max = self.df_controller.loc[self.df_controller['param'] == 'v_max'].value.values[0]
        v_supportability = [v_max > v_modules[0], v_max > v_modules[1]]
        check_voltage_dict = {'param': 'check_voltage', 'value': v_supportability}
        self.df_controller_setup = self.df_controller_setup.append(check_voltage_dict, ignore_index=True)


if __name__ == '__main__':
    path = './Components/components.xlsx'
    df_sys = pd.read_excel(path, sheet_name='system')
    setup = {'param': ['p_min'], 'value': [3.155611]}
    df_set = pd.DataFrame.from_dict(setup)
    df_p = pd.read_excel(path, sheet_name='panels')
    df_c = pd.read_excel(path, sheet_name='controller')
    p = Panels(df_p, df_sys, df_set, df_c)
    controller = Controller(df_c, p)
    print('oi')

