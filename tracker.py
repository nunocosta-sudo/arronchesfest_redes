import os
import time
import datetime
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_instagram_followers(username):
    """Obtém os seguidores usando cookie de sessão com gestão de retentativas (Rate Limit 429)."""
    session_id = os.getenv("INSTA_SESSION_ID")
    
    if not session_id:
        raise Exception("O segredo INSTA_SESSION_ID não foi configurado no GitHub!")

    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-IG-App-ID": "936619743392459",
        "Cookie": f"sessionid={session_id}"
    }

    # Tenta até 3 vezes com intervalo entre tentativas
    for attempt in range(1, 4):
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            return data["data"]["user"]["edge_followed_by"]["count"]
        elif response.status_code == 429:
            print(f"Aviso: Recebido bloqueio 429 (Tentativa {attempt}/3). A aguardar 10 segundos...")
            time.sleep(10)
        else:
            raise Exception(f"Erro no Instagram (Status {response.status_code}): {response.text[:100]}")

    raise Exception("Instagram bloqueou por excesso de pedidos (Status 429) após 3 tentativas.")