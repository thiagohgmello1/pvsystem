import pandas as pd
import matplotlib.pyplot as plt


class ElectricityBill:
    def __init__(self, file, sheet='bill'):
        self.df_bill = pd.read_excel(file, sheet_name=sheet)
        self._daily_consumption_calculation()

    def _daily_consumption_calculation(self):
        self.df_bill['daily_consumption'] = self.df_bill['consumption'] * 1000 / self.df_bill['days_billed']

    def plot_monthly_consumption(self, output_f='outputs/electricity_bill/monthy_c.png'):
        fig, ax = plt.subplots()
        ax.plot(self.df_bill['month_year'], self.df_bill['consumption'])
        plt.xlabel('Mês de faturamento')
        plt.ylabel('Energia (kWh)')
        plt.ylim((0, None))
        plt.title('Consumo Mensal (kWh)')
        plt.savefig(output_f, dpi=80)
        plt.show()

    def plot_daily_consumption(self, output_f='outputs/electricity_bill/daily_c.png'):
        fig, ax = plt.subplots()
        ax.plot(self.df_bill['month_year'], self.df_bill['daily_consumption'])
        plt.xlabel('Mês de faturamento')
        plt.ylabel('Energia (Wh)')
        plt.ylim((0, None))
        plt.title('Consumo diário médio por mês (Wh)')
        plt.savefig(output_f, dpi=80)
        plt.show()


if __name__ == '__main__':
    bill = ElectricityBill('../Bills/test_file.xlsx')
    bill.plot_monthly_consumption()
    bill.plot_daily_consumption()
