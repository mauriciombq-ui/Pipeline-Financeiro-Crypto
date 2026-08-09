import time
import sys
import ccxt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

sys.stdout.reconfigure(line_buffering=True)

# ==============================================================================
# CONFIGURAÇÕES - CREDENCIAIS DO SEU INFLUXDB
# ==============================================================================
TOKEN = "HzcJOSnjCoNb8dOxVVfc-SMh4PnkiurNjGZCHky8Cdw7uik81KJ9AQuDONa9-7erTKkdCL2iX_AKdMpGcQH1Fw=="
ORG = "265147d78b076bda"
BUCKET = "crypto_candles"
URL = "http://localhost:8086"
# ==============================================================================

# LISTA DE MOEDAS ESCALÁVEIS (Adicione quantas quiser aqui)
MOEDAS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']

exchange = ccxt.binance({'enableRateLimit': True, 'timeout': 10000})
client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

print(f"Pipeline escalável iniciado para as moedas: {MOEDAS}", flush=True)

try:
    while True:
        # Varre cada moeda da lista coletando o preço atualizado
        for par in MOEDAS:
            try:
                candles = exchange.fetch_ohlcv(par, timeframe='1m', limit=1)
                
                if candles and len(candles) > 0:
                    candle = candles[0]
                    ticker_limpo = par.replace('/', '') # Transforma BTC/USDT em BTCUSDT
                    
                    point = Point("candles_1m") \
                        .tag("ticker", ticker_limpo) \
                        .tag("exchange", "binance") \
                        .field("open", float(candle[1])) \
                        .field("high", float(candle[2])) \
                        .field("low", float(candle[3])) \
                        .field("close", float(candle[4])) \
                        .field("volume", float(candle[5])) \
                        .time(int(candle[0]) * 1000000)

                    write_api.write(bucket=BUCKET, org=ORG, record=point)
                    print(f"[{time.strftime('%H:%M:%S')}] {ticker_limpo} Gravado! Preço: ${candle[4]:,.2f}", flush=True)
                    
                # Pequena pausa de 1 segundo entre moedas para evitar bloqueio da API
                time.sleep(1)

            except Exception as e:
                print(f"Erro no ativo {par}: {e}", flush=True)
        
        # Aguarda o restante do minuto para a próxima rodada de coleta
        time.sleep(55)

except KeyboardInterrupt:
    print("\nColetor escalável encerrado.", flush=True)
finally:
    client.close()

    # Atualização multi-ativos ok


