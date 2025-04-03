# main.py - メインアプリケーションファイル
import os
import sys
from logger import setup_logger
from config import load_config
from flask import Flask
from teams_webhook import TeamsWebhook
from routes import register_routes

# カレントディレクトリをスクリプトのディレクトリに設定
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# ロガー設定をインポート
logger = setup_logger(script_dir)

# 設定をインポート
config = load_config(script_dir)

# Flaskアプリケーションをインポート
app = Flask(__name__)

# Teams Webhookの初期化
try:
    teams_webhook = None

    if config['TEAMS_WORKFLOW_URL']:
        teams_webhook = TeamsWebhook(config['TEAMS_WORKFLOW_URL'])
        logger.info(f"Teams Webhook初期化完了: {config['TEAMS_WORKFLOW_URL']}")
    else:
        logger.warning("TEAMS_WORKFLOW_URLが設定されていません。Teams通知機能は無効です。")

except ImportError:
    logger.error("teams_webhook モジュールが見つかりません。")
    teams_webhook = None

# ルートの登録
register_routes(app, config, teams_webhook)

# アプリケーション実行
if __name__ == '__main__':
    try:
        logger.info("Ollama連携アプリケーションを起動します")
        logger.info(f"環境: {os.getenv('FLASK_ENV', 'production')}")
        logger.info(f"デバッグモード: {config['DEBUG']}")
        logger.info(f"Ollama URL: {config['OLLAMA_URL']}")
        logger.info(f"Ollama モデル: {config['OLLAMA_MODEL']}")
        logger.info(f"Teams Webhook URL: {config['TEAMS_WORKFLOW_URL'] if config['TEAMS_WORKFLOW_URL'] else '未設定'}")

        # アプリケーションを起動
        logger.info(f"アプリケーションを起動: {config['HOST']}:{config['PORT']}")
        app.run(host=config['HOST'], port=config['PORT'], debug=config['DEBUG'])

    except Exception as e:
        logger.error(f"アプリケーション起動中にエラーが発生しました: {str(e)}")
        raise
