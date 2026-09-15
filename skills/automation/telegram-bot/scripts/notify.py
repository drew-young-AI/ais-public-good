import os
import requests
import json
from dotenv import load_dotenv

# 強制載入指定路徑的環境變數
load_dotenv(dotenv_path=os.path.expanduser("~/.codex/.env"))

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def verify_and_send(message=None, image_path=None):
    if not TOKEN or not CHAT_ID:
        return "錯誤：找不到必要的環境變數 (TOKEN 或 CHAT_ID)"
    
    # 1. 身份握手驗證
    me_url = f"https://api.telegram.org/bot{TOKEN}/getMe"
    try:
        me_resp = requests.get(me_url).json()
    except Exception as e:
        return f"身份握手請求失敗: {str(e)}"
    
    # 2. 發送任務
    try:
        if image_path:
            url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
            with open(image_path, 'rb') as f:
                files = {'photo': f}
                data = {'chat_id': CHAT_ID}
                resp = requests.post(url, files=files, data=data)
        else:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            data = {'chat_id': CHAT_ID, 'text': message}
            resp = requests.post(url, data=data)
        
        # 這裡不應直接存取 resp.text，應該使用 resp.json() 或確保回應已處理
        if resp.status_code == 200:
            return "成功"
        else:
            return f"發送失敗: {resp.status_code} - {resp.text}"
    except Exception as e:
        return f"發送請求失敗: {str(e)}"

if __name__ == "__main__":
    import sys
    # 簡單指令解析
    if len(sys.argv) > 1:
        if sys.argv[1] == "--message":
            print(verify_and_send(message=sys.argv[2]))
        elif sys.argv[1] == "--image":
            print(verify_and_send(image_path=sys.argv[2]))
