import datetime
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_instagram_followers(username):
    """Obtém o número de seguidores públicos de uma conta do Instagram via API web."""
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-IG-App-ID": "936619743392459"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data["data"]["user"]["edge_followed_by"]["count"]

def append_to_sheets(date_str, followers):
    """Lida com a autenticação e adiciona a nova linha ao Google Sheets."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Carrega as credenciais geradas dinamicamente no GitHub Actions
    creds = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
    client = gspread.authorize(creds)
    
    # Abre a folha pelo nome exato
    sheet = client.open("Instagram_Festival_Tracker").sheet1
    
    # Adiciona a linha [Data, Seguidores]
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