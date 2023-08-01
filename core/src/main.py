from storage import upload_file, connect_db, disconnect_db, get_premium_user_list
from constants import TRADE_DATE_FORMAT_STR, OUTPUT_FILE, S3_BUCKET_NAME, S3_DOUBLE_MA_BASE_DIR, TODAY_STR, MAX_STRATEGY_SIGNAL_ERROR_COUNT, LOCAL_BASE_DIR, STRATEGY_DMA_SHORT_TERM, STRATEGY_DMA_LONG_TERM, APP_ENV, FP_SEND_EMAIL_API, USER_LIST
from notification import send_emails_smtp
from strategy.dma.dma_strategy import DMATradeStrategy
from message import generate_message_to_file
from db import DmaTradeSignalModel
from strategy.trade_signal import TradeSignalState
from client.ts_client import TSClient
from market.index_daily import IndexDaily
from os.path import exists
from datetime import datetime, timedelta
import os
import requests
import json


def startup():
    print('make sure local bash path exists...')
    if (not exists(LOCAL_BASE_DIR)):
        os.makedirs(LOCAL_BASE_DIR, exist_ok=True)


def send_emails(address, subject, body):
    data = {"address": address,
            "subject": subject,
            "body": body}
    headers = {'Content-type': 'application/json'}
    r = requests.get(FP_SEND_EMAIL_API, data=json.dumps(data), headers=headers)
    print(r.text)


if __name__ == "__main__":
    startup()

    trade_data_client = TSClient()

    print('start sync index daily trade data...')

    print('start process long etf...')
    title_msg = '==Long ETF==\n'
    dma_strategy = DMATradeStrategy(
        trade_data_client, STRATEGY_DMA_SHORT_TERM, STRATEGY_DMA_LONG_TERM, TODAY_STR)
    dma_strategy.process("data/best_etf.txt")
    generate_message_to_file(dma_strategy, title_msg)

    print('start process other etf...')
    title_msg = '==Other ETF==\n'
    dma_strategy = DMATradeStrategy(
        trade_data_client, STRATEGY_DMA_SHORT_TERM, STRATEGY_DMA_LONG_TERM, TODAY_STR)
    dma_strategy.process("data/fund.txt")
    generate_message_to_file(dma_strategy, title_msg)

    with open(LOCAL_BASE_DIR + OUTPUT_FILE, 'r') as file:
        message = file.read()
        subject = '双均线策略交易信号: ' + TODAY_STR + ' - A股市场'
        send_emails(USER_LIST, subject, message)
