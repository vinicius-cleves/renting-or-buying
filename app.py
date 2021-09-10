import pandas as pd
import plotly.express as px
import streamlit as st

from renting_or_buying import SAC, Aluguel, Financiamento

st.title('Comprar ou alugar?')
st.caption('Isso não é aconselhamento financeiro!')
st.text('Series no gráfico:')

st.sidebar.header('Opções da simulação')
V = 1
pct_entrada = st.sidebar.slider('Entrada (%)', 0, 100) / 100
c_a = st.sidebar.slider('Custo proporcional (%) do aluguel', .0, 1., .5) / 100
t_j = st.sidebar.slider('Taxa de juros (%) do emprestimo', 0., 50., 7.8) / 100
n = 12 * st.sidebar.slider('Anos do emprestimo', 1, 30, 20)

t_r = st.sidebar.slider('Taxa de retorno (%) do ativo livre de risco (selic)', 0., 30., 5.25) / 100
t_i = st.sidebar.slider('Taxa de retorno (%) valorização imobiliaria', 0., 50., 9.6) / 100
t_m = st.sidebar.slider('Taxa de retorno (%) investimento', 0., 50., 12.) / 100


al = Aluguel(V=V, c_a=c_a, t_r=t_r, t_i=t_i, t_m=t_m, amortizador=SAC(pct_entrada=pct_entrada, t_j=t_j, n=n))
al_parcelas, al_investimentos, al_total, al_pagamentos, al_recebidos = al.run_simulation()

f = Financiamento(V=V, t_r=t_r, t_i=t_i, amortizador=SAC(pct_entrada=pct_entrada, t_j=t_j, n=n))
f_parcelas, f_imovel, f_total, f_pagamentos, f_recebidos = f.run_simulation()

plot_options = {
  'Aluguel':{
    'data': al_total,
    'show': True
  },
  'Aluguel: pagamentos':{
    'data':  al_parcelas,
    'show': False
  },
  'Aluguel: investimentos':{
    'data':  al_investimentos,
    'show': False
  }, 
  'Financiamento':{
    'data':  f_total,
    'show': True
  },
  'Financiamento: pagamentos':{
    'data':  f_parcelas,
    'show': False
  },
  'Financiamento: imovel':{
    'data':  f_imovel,
    'show': False
  },
}

cols = st.columns(3)
plot_data = {}
for i, (key, value) in enumerate(plot_options.items()):
  col = cols[ i % len(cols)]
  if col.checkbox(key, value['show']):
    plot_data[key] = value['data']

df = pd.DataFrame(plot_data)

df = (
  df
  .rename_axis(index='Mês')
  .reset_index()
  .melt(id_vars=['Mês'], var_name='Estratégia', value_name='Valor Presente'))


cf = (
  pd.DataFrame({
    'Aluguel: Pagamentos': al_pagamentos,
    'Aluguel: Recebimentos': al_recebidos,
    'Financiamento: Pagamentos': f_pagamentos,
    'Financiamento: Recebimentos': f_recebidos 
  })
  .rename_axis(index='Mês')
  .reset_index())
cf['Ano'] = (cf['Mês'] - 1) // 12 + 1
cf = (
  cf
  .drop(columns='Mês')
  .groupby('Ano')
  .sum()
  .reset_index()
  .melt(id_vars=['Ano'], var_name='Elemento', value_name='Valor')
)


fig = px.line(
  df, 
  x='Mês', 
  y='Valor Presente', 
  color='Estratégia', 
  title='Evolução do Patrimônio',
  template="plotly_white"
)
fig.update_layout(
    yaxis_title="VP do patrimônio",
    legend_title="Legenda",
    legend=dict(font=dict(size=8)),
    font=dict(size=10),
    title=dict(font=dict(size=22)),
    margin=dict(l=0, r=0),
    plot_bgcolor='rgba(0,0,0,0)',
)
st.plotly_chart(fig)

fig2 = px.bar(
  cf, 
  x='Ano', 
  y='Valor', 
  color='Elemento', 
  barmode='group',
  template="plotly_white",
  title='Fluxo de Caixa')
fig2.update_layout(
    legend=dict(font=dict(size=8)),
    font=dict(size=10),
    title=dict(font=dict(size=22)),
    margin=dict(l=0, r=0),
    plot_bgcolor='rgba(0,0,0,0)',   
)
st.plotly_chart(fig2)

st.header('Matemática')
with open('explanation.txt') as f:
  st.markdown(f.read())
