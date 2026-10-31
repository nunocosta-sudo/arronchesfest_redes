import datetime
import json
import os
import sys

import gspread
import requests

INSTAGRAM_ACCOUNT = "festivalarronches"
SHEET_NAME = "Instagram_Festival_Tracker"


def get_instagram_followers():
    """Obtém os seguidores através da API oficial do Instagram."""
    # Modo de teste: permite validar o Google Sheet antes de teres o token
    fake = os.getenv("FAKE_FOLLOWERS")
    if fake:
        print("Aviso: a usar FAKE_FOLLOWERS (modo de teste).")
        return int(fake)

    token = os.getenv("INSTA_TOKEN")
    if not token:
        raise RuntimeError("O secret INSTA_TOKEN não foi configurado no GitHub!")

    response = requests.get(
        "https://graph.instagram.com/v23.0/me",
        params={"fields": "username,followers_count", "access_token": token},
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Erro na API do Instagram (Status {response.status_code}): {response.text[:200]}"
        )

    data = response.json()

    # Confirma que o token pertence mesmo à conta esperada
    if data.get("username", "").lower() != INSTAGRAM_ACCOUNT.lower():
        raise RuntimeError(
            f"O token pertence a '{data.get('username')}', não a '{INSTAGRAM_ACCOUNT}'."
        )

    return data["followers_count"]


def append_to_sheets(date_str, followers):
    """Autentica com a service account e adiciona uma linha ao Google Sheets."""
    creds_dict = json.loads(os.environ["GOOGLE_CREDS"])
    client = gspread.service_account_from_dict(creds_dict)
    sheet = client.open(SHEET_NAME).sheet1
    sheet.append_row([date_str, followers], value_input_option="USER_ENTERED")


if __name__ == "__main__":
    today = datetime.date.today().strftime("%d/%m/%Y")

    try:
        followers_count = get_instagram_followers()
        append_to_sheets(today, followers_count)
        print(f"[{today}] Sucesso: {followers_count} seguidores registados para '{INSTAGRAM_ACCOUNT}'.")
    except Exception as e:
        print(f"Erro ao executar o tracking: {e}")
        sys.exit(1)  # faz o workflow falhar (e avisar-te) em vez de parecer sucesso