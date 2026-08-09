import time
import sys
import pandas as pd
from influxdb_client import InfluxDBClient

# Garante que o terminal printe as mensagens na hora
sys.stdout.reconfigure(line_buffering=True)

# ==============================================================================
# CONFIGURAÇÕES DO SEU INFLUXDB
# ==============================================================================
TOKEN = "HzcJOSnjCoNb8dOxVVfc-SMh4PnkiurNjGZCHky8Cdw7uik81KJ9AQuDONa9-7erTKkdCL2iX_AKdMpGcQH1Fw=="
ORG = "265147d78b076bda"
BUCKET = "crypto_candles"
URL = "http://localhost:8086"
# ==============================================================================

print("Iniciando o cérebro do robô...", flush=True)

try:
    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
    query_api = client.query_api()
    print("Conectado ao InfluxDB com sucesso!", flush=True)
except Exception as e:
    print(f"Erro ao conectar no InfluxDB: {e}", flush=True)
    sys.exit(1)

# Query Flux ajustada para garantir compatibilidade com o Pandas DataFrame
query = f'''
from(bucket: "{BUCKET}")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "candles_1m")
  |> filter(fn: (r) => r["ticker"] == "BTCUSDT")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
'''

print("Aguardando os primeiros sinais da estratégia...", flush=True)

try:
    while True:
        try:
            # 1. Puxa os dados do InfluxDB
            df = query_api.query_data_frame(org=ORG, query=query)
            
            # Se o InfluxDB retornar uma lista de DataFrames, pegamos o primeiro
            if isinstance(df, list):
                df = df[0] if len(df) > 0 else pd.DataFrame()
            
            if df is not None and not df.empty:
                # Remove colunas desnecessárias que o Influx traz por padrão
                colunas_uteis = [c for c in ['_time', 'close', 'open', 'high', 'low', 'volume'] if c in df.columns]
                df = df[colunas_uteis]
                
                # Organiza por ordem cronológica
                df = df.sort_values(by='_time').reset_index(drop=True)
                
                # 2. CALCULA A MÉDIA MÓVEL (Últimos 5 minutos para o teste ser mais rápido)
                df['media_fast'] = df['close'].rolling(window=5).mean()
                
                ultimo_preco = float(df['close'].iloc[-1])
                ultima_media = df['media_fast'].iloc[-1]
                
                # 3. VERIFICAÇÃO DE SINAL
                if not pd.isna(ultima_media):
                    ultima_media = float(ultima_media)
                    print(f"[{time.strftime('%H:%M:%S')}] BTC: ${ultimo_preco:,.2f} | Média 5m: ${ultima_media:,.2f}", flush=True)
                    
                    if ultimo_preco > ultima_media:
                        print(" 🟢 SINAL: Preço ACIMA da média. Tendência de ALTA (Comprar)", flush=True)
                    else:
                        print(" 🔴 SINAL: Preço ABAIXO da média. Tendência de BAIXA (Vender/Aguardar)", flush=True)
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] Coletando dados... Temos {len(df)} minutos salvos. Precisamos de pelo menos 5.", flush=True)
            else:
                print(f"[{time.strftime('%H:%M:%S')}] O InfluxDB retornou uma tabela vazia. O app.py está salvando dados?", flush=True)

        except Exception as erro_interno:
            print(f"Erro durante a execução da estratégia: {erro_interno}", flush=True)

        # O robô reavalia o gráfico a cada 15 segundos
        time.sleep(15)

except KeyboardInterrupt:
    print("\nRobô de estratégia desligado pelo usuário.", flush=True)
finally:
    client.close()
