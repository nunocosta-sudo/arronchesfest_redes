import datetime
import json
import re
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_instagram_followers(username):
    """Obtém os seguidores tentando primeiro o Picuki (espelho público) e depois a web API do Instagram."""
    
    # 1. Tentativa via Picuki (método mais estável para GitHub Actions)
    try:
        url = f"https://www.picuki.com/profile/{username}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            match = re.search(r'<span class="followed_by">([0-9,\.\s]+)</span>', res.text)
            if match:
                raw_num = match.group(1).replace(',', '').replace('.', '').strip()
                return int(raw_num)
    except Exception as e:
        print(f"Aviso: Tentativa Picuki falhou ({e}), a tentar método alternativo...")

    # 2. Tentativa via endpoint alternativo com cabeçalhos de mobile
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "User-Agent": "Instagram 219.0.0.12.117 Android",
        "X-IG-App-ID": "936619743392459"
    }
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        return data["data"]["user"]["edge_followed_by"]["count"]

    raise Exception(f"Não foi possível extrair os seguidores do perfil @{username}.")

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