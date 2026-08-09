import time
import sys
import pandas as pd
from influxdb_client import InfluxDBClient

sys.stdout.reconfigure(line_buffering=True)

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

# Query Flux atualizada: Removemos o filtro de ticker fixo para trazer todas as moedas de uma vez
query = f'''
from(bucket: "{BUCKET}")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "candles_1m")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
'''

print("Cérebro Multi-Ativos iniciado...", flush=True)

try:
    while True:
        df = query_api.query_data_frame(org=ORG, query=query)
        
        if isinstance(df, list):
            df = pd.concat(df) if len(df) > 0 else pd.DataFrame()
            
        if df is not None and not df.empty:
            # O SEGREDO DA ESCALABILIDADE: Agrupar por ticker antes de calcular a média
            for ticker, dados_moeda in df.groupby('ticker'):
                
                # Organiza o histórico da moeda específica por tempo
                dados_moeda = dados_moeda.sort_values(by='_time').reset_index(drop=True)
                
                # Calcula a média móvel de 5 minutos para esta moeda
                dados_moeda['media_5m'] = dados_moeda['close'].rolling(window=5).mean()
                
                ultimo_preco = float(dados_moeda['close'].iloc[-1])
                ultima_media = dados_moeda['media_5m'].iloc[-1]
                
                if not pd.isna(ultima_media):
                    print(f"[{time.strftime('%H:%M:%S')}] {ticker} | Preço: ${ultimo_preco:,.2f} | Média 5m: ${ultima_media:,.2f}", flush=True)
                    if ultimo_preco > ultima_media:
                        print(f" 🟢 SINAL {ticker}: ALTA (Comprar)")
                    else:
                        print(f" 🔴 SINAL {ticker}: BAIXA (Aguardar)")
            print("-" * 50)
        else:
            print("Aguardando dados no InfluxDB...")

        # Reavalia o mercado a cada 20 segundos
        time.sleep(20)

except KeyboardInterrupt:
    print("\nRobô multi-ativos desligado.", flush=True)
finally:
    client.close()

