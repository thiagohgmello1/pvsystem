import pandas as pd

from controllers.panels import Panels


class Controller:
    def __init__(self, df_controller, panels: Panels):
        self.df_controller = df_controller
        self.df_controller_setup = pd.DataFrame(columns=['param', 'value'])
        self._supportability(panels.df_panels, panels.df_panels_setup)


    def _supportability(self, df_panels, df_panels_setup):
        i_pmax = df_panels.loc[df_panels['param'] == 'i_pmax'].value.values[0]
        parallel_controllers = self.df_controller.loc[self.df_controller['param'] == 'parallel_controllers'].value.\
            values[0]
        i_controller = self.df_controller.loc[self.df_controller['param'] == 'i_load'].value.values[0]
        min_parallel, max_parallel = df_panels_setup.loc[df_panels_setup['param'] == 'mppt_parallel'].value.values[0]
        min_supportability = True if min_parallel * i_pmax < i_controller * parallel_controllers else False
        max_supportability = True if max_parallel * i_pmax < i_controller * parallel_controllers else False
        supportability_dict = {'param': 'supportability', 'value': [min_supportability, max_supportability]}
        self.df_controller_setup = self.df_controller_setup.append(supportability_dict, ignore_index=True)


if __name__ == '__main__':
    path = './Components/components.xlsx'
    df_sys = pd.read_excel(path, sheet_name='system')
    setup = {'param': ['p_min'], 'value': [3.155611]}
    df_set = pd.DataFrame.from_dict(setup)
    df_p = pd.read_excel(path, sheet_name='panels')
    df_c = pd.read_excel(path, sheet_name='controller')
    p = Panels(df_p, df_sys, df_set, df_c)
    controller = Controller(df_c, p)
