# async_processor.py - 直接通信版非同期処理
import logging
import traceback
from ollama_client import generate_ollama_response

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 詳細なログを有効化

def process_query_async(query_text, original_data, ollama_url, ollama_model, ollama_timeout, teams_webhook):
    """
    クエリを非同期で処理し、結果をTeamsに通知する

    Args:
        query_text: 処理するクエリテキスト
        original_data: 元のTeamsリクエストデータ
        ollama_url: OllamaのURL
        ollama_model: 使用するOllamaモデル
        ollama_timeout: リクエストのタイムアウト時間（秒）
        teams_webhook: Teams Webhookインスタンス
    """
    try:
        # Ollamaで回答を生成
        response = generate_ollama_response(query_text, ollama_url, ollama_model, ollama_timeout)
        logger.info(f"非同期処理による応答生成完了: {response[:100]}...")

        # クリーンなクエリを抽出
        clean_query = query_text.replace('ollama質問', '').strip()

        if teams_webhook:
            # TEAMS_WORKFLOW_URLを使用して直接Teamsに送信
            logger.info("Teamsに直接応答を送信します")
            result = teams_webhook.send_ollama_response(clean_query, response)
            logger.info(f"Teams送信結果: {result}")

            # 送信に失敗した場合の処理
            if result.get("status") == "error":
                logger.error(f"Teams送信エラー: {result.get('message', 'unknown error')}")
                # エラー発生時は何もしない（すでにログに記録済み）

        else:
            logger.error("Teams Webhookが設定されていないため、通知できません")

    except Exception as e:
        logger.error(f"非同期処理中にエラーが発生しました: {str(e)}")
        logger.error(traceback.format_exc())
