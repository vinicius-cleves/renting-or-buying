import numpy as np

class SistemaDeAmortizacao:
    pass

def anual_to_month_rate(rate):
    return (1 + rate)**(1/12) - 1
    
class SAC(SistemaDeAmortizacao):
    def __init__(self, pct_entrada, t_j, n):
        self.pct_entrada = pct_entrada
        self.t_j = anual_to_month_rate(t_j)
        self.n = n
    
    def parcela(self, V, i):
        assert 0 <= i <= self.n

        if i == 0: 
            return - self.pct_entrada * V
        
        valor_financiado = V * (1 - self.pct_entrada)
        amortizacao = valor_financiado/self.n
        valor_amortizado = (valor_financiado/self.n)*(i-1)
        saldo_anterior = valor_financiado - valor_amortizado
        juros = saldo_anterior * self.t_j
        return - (amortizacao + juros)
    
    def parcelas(self, V):
        return [self.parcela(V, i) for i in range(self.n + 1)]
    
    def propriedade(self, V, i):
        return V * (self.pct_entrada + (1 - self.pct_entrada) * i / self.n)     

class SimuladorFinanceiro:
    def __init__(self, t_r):
        self.t_r = t_r

    def valor_presente(self, valor, periodos, montly_rate=None):
        montly_rate = montly_rate if montly_rate is not None else self.t_r
        return valor/((1 + montly_rate) ** periodos)
    
    def valor_futuro(self, valor, periodos, montly_rate=None):
        montly_rate = montly_rate if montly_rate is not None else self.t_r
        return valor * (1 + montly_rate) ** periodos

class Financiamento(SimuladorFinanceiro):
    def __init__(self, V, t_r, t_i, amortizador):
        self.V = V
        self.n = amortizador.n
        self.t_r = anual_to_month_rate(t_r)
        self.t_i = anual_to_month_rate(t_i)
        
        self.amortizador = amortizador
     
    def run_simulation(self):
        parcelas = self.amortizador.parcelas(self.V)
        VP_parcelas = np.cumsum([self.valor_presente(parcela, i) 
                       for i, parcela in enumerate(parcelas)]).tolist()
        
        VP_imovel = [
            self.valor_presente(
                self.valor_futuro(self.amortizador.propriedade(self.V, i), i, self.t_i), 
                i)
            for i in range(self.n+1)]
        
        VP_total = list(map(sum, zip(VP_parcelas, VP_imovel)))
        recebidos = [0] * (len(parcelas) - 1) + [self.valor_futuro(VP_imovel[-1], self.n)]
        return VP_parcelas, VP_imovel, VP_total, parcelas, recebidos
    

class Aluguel(SimuladorFinanceiro):
    def __init__(self, V, c_a, t_r, t_i, t_m, amortizador):
        
        self.V = V
        self.n = amortizador.n
        self.c_a = c_a
        self.t_r = anual_to_month_rate(t_r)
        self.t_i = anual_to_month_rate(t_i)
        self.t_m = anual_to_month_rate(t_m)
        self.amortizador = amortizador
     
    def run_simulation(self):
        # self.parcelas = self.amortizador.parcelas(self.V)
        # self.investimentos = self.calc_investimentos()
        parcelas, investimentos = self.calc_parcelas_e_investimentos()
        VP_parcelas = np.cumsum([self.valor_presente(parcela, i) 
                       for i, parcela in enumerate(parcelas)]).tolist()
        
        VP_investimentos = []
        for _n in range(self.n + 1):
            VP_investimentos.append(
                sum(self.valor_presente(
                        self.valor_futuro(investimento, _n - i, self.t_m), 
                        _n
                    ) 
                    for i, investimento in enumerate(investimentos[: _n + 1])
                )
            )
        assert all([val >= 0 for val in VP_investimentos]), (
            'Esse cenario não pode ser simulado pois o valor do investimento vai ser inferior ao gasto '
            'com aluguel'
        )
        
        VP_total = list(map(sum, zip(VP_parcelas, VP_investimentos)))
        recebidos = [0] * (len(VP_investimentos) - 1) +  [self.valor_futuro(VP_investimentos[-1], self.n)]
        return VP_parcelas, VP_investimentos, VP_total, parcelas, recebidos
      
    def calc_aluguel(self, i):
        return self.valor_futuro(- self.c_a * self.V, i, self.t_i)
    
    def calc_parcela_e_investimento(self, i):
        parcela_fin = self.amortizador.parcela(self.V, i)
        aluguel = self.calc_aluguel(i)
        parcela = min(parcela_fin, aluguel)
        investimento = - parcela + aluguel
        
        return parcela, investimento
    
    def calc_parcelas_e_investimentos(self):
        parcelas, investimentos = tuple(zip(*[self.calc_parcela_e_investimento(i) for i in range(self.n + 1)]))
        return parcelas, investimentos







