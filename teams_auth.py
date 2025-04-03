# teams_auth.py - Teams認証関連の機能
import logging
import hmac
import hashlib

logger = logging.getLogger(__name__)

def verify_teams_token(request_data, signature, teams_outgoing_token):
    """
    Teamsからのリクエストの署名を検証する

    Args:
        request_data: リクエストの生データ
        signature: Teamsからの署名
        teams_outgoing_token: Teams Outgoing Token

    Returns:
        bool: 署名が有効な場合True
    """
    if not teams_outgoing_token:
        logger.error("Teams Outgoing Tokenが設定されていません")
        return False

    # 署名はHMACプレフィックス付きで送られてくる可能性があるのでクリーンアップ
    if signature and signature.startswith('HMAC '):
        signature = signature[5:]  # 'HMAC 'の部分を削除

    logger.debug(f"認証トークン: {teams_outgoing_token[:5]}... (一部のみ表示)")
    logger.debug(f"受信した署名: {signature}")

    try:
        # 実際のHMAC計算
        computed_hmac = hmac.new(
            key=teams_outgoing_token.encode('utf-8'),
            msg=request_data,
            digestmod=hashlib.sha256
        ).hexdigest()

        logger.debug(f"計算したHMAC: {computed_hmac}")

        # 署名を比較
        return hmac.compare_digest(computed_hmac, signature)

    except Exception as e:
        logger.error(f"署名検証中にエラーが発生しました: {str(e)}")
        return False
