import datetime
import instaloader
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_instagram_followers(username):
    """Extrai o número de seguidores públicos de uma conta de Instagram."""
    L = instaloader.Instaloader()
    profile = instaloader.Profile.from_username(L.context, username)
    return profile.followers

def append_to_sheets(date_str, followers):
    """Liga à API do Google Sheets e adiciona uma nova linha."""
    # Definição dos permissões da API do Google
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Carrega as credenciais a partir do ficheiro de chave da Service Account
    creds = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
    client = gspread.authorize(creds)
    
    # Abre a folha de cálculo pelo nome
    sheet = client.open("Instagram_Festival_Tracker").sheet1
    
    # Adiciona a nova linha [Data, Seguidores]
    sheet.append_row([date_str, followers])

if __name__ == "__main__":
    # NOME DA PÁGINA DO FESTIVAL
    INSTAGRAM_ACCOUNT = "festivalarronches" 
    
    today = datetime.date.today().strftime("%d/%m/%Y")
    
    try:
        followers_count = get_instagram_followers(INSTAGRAM_ACCOUNT)
        append_to_sheets(today, followers_count)
        print(f"[{today}] Sucesso: {followers_count} seguidores registados.")
    except Exception as e:
        print(f"Erro ao executar o tracking: {e}")