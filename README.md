# 📈 Pipeline de Dados Financeiros e Robô de Trading com InfluxDB

Este é um projeto de engenharia de dados que adapta conceitos industriais (IoT/Séries Temporais) para o mercado financeiro de criptomoedas, focado em alta performance, escalabilidade e tomada de decisão automatizada.

## 🛠️ Tecnologias Utilizadas
* **Python**: Linguagem base para os scripts de automação.
* **InfluxDB (TSDB)**: Banco de dados de séries temporais para armazenamento otimizado de dados OHLCV (Candles).
* **CCXT**: Biblioteca padrão ouro para conexão robusta com APIs de exchanges (Binance).
* **Pandas**: Biblioteca para cálculos matemáticos e análise de dados quantitativos.

## 📐 Estrutura do Pipeline
1. `app.py`: Coletor automatizado que puxa dados de 1 minuto do Bitcoin (BTC/USDT) via WebSocket/REST e injeta no InfluxDB.
2. `estrategia.py`: Cérebro do robô que lê o InfluxDB em tempo real, calcula uma Média Móvel de curto prazo e gera sinais de Compra e Venda.
3. `backtest.py`: Simulador histórico que valida a performance e o lucro/prejuízo da estratégia com dados passados armazenados no banco.
