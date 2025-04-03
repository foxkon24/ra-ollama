# routes.py - Flaskルート定義
import re
import logging
import threading
import traceback
from datetime import datetime
from flask import request, jsonify, render_template
from teams_auth import verify_teams_token
from async_processor import process_query_async
import requests

logger = logging.getLogger(__name__)

def register_routes(app, config, teams_webhook):
    """
    Flaskアプリにルートを登録する

    Args:
        app: Flaskアプリインスタンス
        config: 設定辞書
        teams_webhook: Teams Webhookインスタンス
    """

    @app.route('/webhook', methods=['POST'])
    def teams_webhook_handler():
        """
        Teamsからのwebhookリクエストを処理する（非同期応答版）
        """
        try:
            logger.info("Webhookリクエストを受信しました")
            logger.info(f"リクエストヘッダー: {request.headers}")
            logger.info(f"リクエストデータ: {request.get_data()}")

            # テスト用：署名検証をスキップ
            skip_verification = True  # 一時的にTrueに設定

            # Teamsからの署名を検証
            signature = request.headers.get('Authorization')
            if not skip_verification and not verify_teams_token(request.get_data(), signature, config['TEAMS_OUTGOING_TOKEN']):
                logger.error("署名の検証に失敗しました")
                return jsonify({"error": "Unauthorized"}), 403

            data = request.json
            logger.info(f"処理するデータ: {data}")

            # Teamsからのメッセージを取得
            if 'text' in data:
                # HTMLタグを除去（Teams形式対応）
                query_text = re.sub(r'<.*?>|\r\n', ' ', data['text'])
                logger.info(f"整形後のクエリ: {query_text}")

                # 非同期で処理を行うためにスレッドを起動
                thread = threading.Thread(
                    target=process_query_async,
                    args=(query_text, data, config['OLLAMA_URL'], config['OLLAMA_MODEL'], 
                          config['OLLAMA_TIMEOUT'], teams_webhook)
                )
                thread.daemon = True  # メインスレッド終了時に一緒に終了
                thread.start()

                # すぐに応答を返す (Teams Outgoing Webhookタイムアウト回避)
                return jsonify({
                    "type": "message",
                    "text": "リクエストを受け付けました。回答を生成中です..."
                })

            else:
                logger.error("テキストフィールドが見つかりません")
                return jsonify({"error": "テキストフィールドが見つかりません"}), 400

        except Exception as e:
            logger.error(f"Webhookの処理中にエラーが発生しました: {str(e)}")
            # スタックトレースをログに記録
            logger.error(traceback.format_exc())
            return jsonify({"error": str(e)}), 500

    @app.route('/health', methods=['GET'])
    def health_check():
        """
        システムの健全性を確認するエンドポイント
        """
        try:
            # Ollamaサーバーの状態を確認
            try:
                ollama_status = requests.get(config['OLLAMA_URL'].replace("/api/generate", "/api/version"), timeout=5).status_code == 200
            except:
                ollama_status = False

            # Teams Webhookの状態を確認
            teams_webhook_status = config['TEAMS_WORKFLOW_URL'] is not None and teams_webhook is not None

            return jsonify({
                "status": "ok" if ollama_status else "degraded",
                "timestamp": datetime.now().isoformat(),
                "system": "Ollama Direct System",
                "ollama_status": "connected" if ollama_status else "disconnected",
                "teams_webhook_status": "configured" if teams_webhook_status else "not configured",
                "model": config['OLLAMA_MODEL']
            })

        except Exception as e:
            logger.error(f"ヘルスチェック中にエラーが発生しました: {str(e)}")
            return jsonify({
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }), 500

    @app.route('/', methods=['GET'])
    def index():
        try:
            return render_template('index.html')
        except:
            return "Ollama Webhook System is running!"
