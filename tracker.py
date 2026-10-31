import datetime
import json
import re
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_instagram_followers(username):
    """Obtém o número de seguidores públicos extraindo do HTML público da conta."""
    url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Instagram respondeu com status {response.status_code}")
        
    # Procura a meta tag de descrição que contém a contagem de seguidores
    # Exemplo: "1,234 Followers, 500 Following..."
    match = re.search(r'meta content="([0-9.,KMBkmb]+)\s+Followers', response.text)
    
    if match:
        raw_count = match.group(1).replace(',', '').replace('.', '')
        return int(raw_count)
    
    # Fallback via endpoint de API web com headers completos
    api_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    api_headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "X-IG-App-ID": "936619743392459"
    }
    api_res = requests.get(api_url, headers=api_headers)
    
    if api_res.status_code == 200:
        data = api_res.json()
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