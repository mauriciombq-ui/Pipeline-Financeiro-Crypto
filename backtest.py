import pandas as pd
from influxdb_client import InfluxDBClient

# ==============================================================================
# CONFIGURAÇÕES DO SEU INFLUXDB
# ==============================================================================
TOKEN = "HzcJOSnjCoNb8dOxVVfc-SMh4PnkiurNjGZCHky8Cdw7uik81KJ9AQuDONa9-7erTKkdCL2iX_AKdMpGcQH1Fw=="
ORG = "265147d78b076bda"
BUCKET = "crypto_candles"
URL = "http://localhost:8086"
# ==============================================================================

client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
query_api = client.query_api()

# Buscaremos as últimas 24h de dados acumulados no banco para o teste
query = f'''
from(bucket: "{BUCKET}")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_measurement"] == "candles_1m")
  |> filter(fn: (r) => r["ticker"] == "BTCUSDT")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
'''

print("📊 Carregando dados históricos do InfluxDB para Backtesting...")
df = query_api.query_data_frame(org=ORG, query=query)

if df is not None and not df.empty:
    # Organiza os dados cronologicamente
    df = df.sort_values(by='_time').reset_index(drop=True)
    
    # Calcula a média móvel de 5 minutos no histórico completo
    df['media_50m'] = df['close'].rolling(window=50).mean()
    df = df.dropna().reset_index(drop=True)

    # Configuração da Simulação Financeira
    capital_inicial = 10000.00  # Começamos com 10 mil dólares virtuais
    capital_atual = capital_inicial
    quantidade_btc = 0.0
    posicionado = False  # False = Fora do mercado, True = Comprado
    total_operacoes = 0

    print(f"Iniciando simulação com Capital Inicial de: ${capital_inicial:,.2f}\n")

    # Varre o passado minuto a minuto simulando o robô operando
    for i in range(len(df)):
        preco_atual = float(df['close'].iloc[i])
        media_atual = float(df['media_50m'].iloc[i])
        horario = df['_time'].iloc[i]

        # Condição de COMPRA: Preço cruzou acima da média e o robô está com dinheiro parado
        if preco_atual > media_atual and not posicionado:
            quantidade_btc = capital_atual / preco_atual
            capital_atual = 0.0
            posicionado = True
            total_operacoes += 1
            print(f"🟢 [COMPRA SIMULADA] {horario} | BTC: ${preco_atual:,.2f} | Investido todo o capital.")

        # Condição de VENDA: Preço caiu abaixo da média e o robô está posicionado em BTC
        elif preco_atual < media_atual and posicionado:
            capital_atual = quantidade_btc * preco_atual
            quantidade_btc = 0.0
            posicionado = False
            total_operacoes += 1
            print(f"🔴 [VENDA SIMULADA]  {horario} | BTC: ${preco_atual:,.2f} | Saldo em caixa: ${capital_atual:,.2f}")

    # Se terminou o histórico ainda comprado, força a venda para fechar a conta
    if posicionado:
        capital_atual = quantidade_btc * float(df['close'].iloc[-1])
        total_operacoes += 1

    # RELATÓRIO FINAL EMPRESARIAL
    lucro_final = capital_atual - capital_inicial
    retorno_percentual = (lucro_final / capital_inicial) * 100

    print("\n" + "="*50)
    print("📈 RELATÓRIO FINAL DE PERFORMANCE DO ROBÔ")
    print("="*50)
    print(f"Capital Inicial:     ${capital_inicial:,.2f}")
    print(f"Capital Final:       ${capital_atual:,.2f}")
    print(f"Lucro/Prejuízo Líquido: ${lucro_final:,.2f} ({retorno_percentual:+.2f}%)")
    print(f"Total de Operações Realizadas: {total_operacoes}")
    print("="*50)

else:
    print("❌ Erro: Não há dados históricos suficientes no banco para rodar o teste.")

client.close()
