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

def append_to_sheets(date_str, followers):
    """Lida com a autenticação e adiciona a nova linha ao Google Sheets."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    creds = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Instagram_Festival_Tracker").sheet1
    sheet.append_row([date_str, followers])

if __name__ == "__main__":
    INSTAGRAM_ACCOUNT = "festivalarronches" 
    today = datetime.date.today().strftime("%d/%m/%Y")
    
    try:
        followers_count = get_instagram_followers(INSTAGRAM_ACCOUNT)
        append_to_sheets(today, followers_count)
        print(f"[{today}] Sucesso: {followers_count} seguidores registados para '{INSTAGRAM_ACCOUNT}'.")
    except Exception as e:
        print(f"Erro ao executar o tracking: {e}")