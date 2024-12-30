# import dependencies to work with scraper
from utils.scraper import get_price

# Import config and google dependencies
from configparser import ConfigParser
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

import warnings
import os

# Just remove warning about the loop
warnings.filterwarnings("ignore", category=DeprecationWarning, message="")

def main():

    # Read config file
    config = ConfigParser()
    config_path = 'constants/config.ini'

    # Check if config file exists and read it
    if os.path.exists(config_path):
        config.read(config_path, encoding='utf-8')
    else:
        print("Файл конфигурации не найден!")
        input()
        exit()

    # Define sheet ID and sheet name from the config file
    sheet_id = config['Data']['SHEET_ID']
    sheet_name = config['Data']['SHEET_NAME'] # Added to get the sheet name from config

    # IMPORTANT: Get the credentials from the https://console.cloud.google.com/
    creds = Credentials.from_service_account_file(config['Data']['CLIENT_JSON'], scopes=['https://www.googleapis.com/auth/spreadsheets'])

    # Initialize Google Sheets API
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    # Get the sheet ID by its name
    try:
        sheet_id_by_name = get_sheet_id_by_name(service, sheet_id, sheet_name)
        print(f"Лист '{sheet_name}' найден! ID листа: {sheet_id_by_name}")
    except ValueError as e:
        print(e)
        return

    # Define the range for the sheet (use the found sheet name)
    range_sheet = f"{sheet_name}!A1:Z1000"

    # Try to access the spreadsheet
    try:
        # Get the result and rows of the sheet
        result = sheet.values().get(spreadsheetId=sheet_id, range=range_sheet).execute()
        rows = result.get('values', [])

    # Catch any access issues
    except Exception as e:
        print("Скрипт не может получить доступ к таблицам! Пожалуйста, проверьте ID и доступ и попробуйте ещё раз")
        return

    # Check if data exists
    if not rows:
        print("Нет ссылок в таблице!")
        return

    # Lists for updates and formatting requests
    updates = []
    format_requests = []

    # Check each row with specified index
    for index, row in enumerate(rows):
        if row:
            print(f"Проверено {index} товаров", end='\r')

            # Get the first link of the product
            link = row[0]
            price_cell = row[1] if len(row) > 1 else None

            if price_cell:
                print(f"Цена уже указана для товара, пропускаем {index + 1}", end='\n')
                continue

            # Get the price using the scraper
            price = get_price(link)

            # Append updates for this product
            updates.append({
                'range': f"{sheet_name}!B{index + 1}",
                'values': [[price]]
            })

            # Format the cell with a new background color
            format_requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id_by_name,
                        'startRowIndex': index,
                        'endRowIndex': index + 1,
                        'startColumnIndex': 1,
                        'endColumnIndex': 2
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {
                                'red': 137/255,
                                'green': 204/255,
                                'blue': 155/255
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor)'
                }
            })

    # If there are updates, send them to the sheet
    if updates:
        body = {
            'valueInputOption': 'RAW',  # RAW to enter the value "as-is"
            'data': updates
        }

        # Push updates to the spreadsheet
        sheet.values().batchUpdate(spreadsheetId=sheet_id, body=body).execute()
        print("Данные успешно получены!")

        # Apply formatting
        if format_requests:
            format_body = {
                'requests': format_requests
            }
            sheet.batchUpdate(spreadsheetId=sheet_id, body=format_body).execute()

    else:
        print("Нет новых цен для обновления!", end='\n')


# Function to get the sheet ID by name
def get_sheet_id_by_name(service, spreadsheet_id, sheet_name):
    # Get metadata about the spreadsheet
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = spreadsheet.get('sheets', [])

    # Loop through all sheets and find the one with the specified name
    for sheet in sheets:
        if sheet['properties']['title'] == sheet_name:
            return sheet['properties']['sheetId']  # Return the sheet ID

    # Raise error if the sheet was not found
    raise ValueError(f"Лист с именем '{sheet_name}' не найден.")

if __name__ == "__main__":
    config = ConfigParser()
    path = "constants/config.ini"

    # Check if the config file exists
    if os.path.exists(path):
        config.read(path)
    else:
        print("Файл конфигурации не найден!")
        input()
        exit()

    # Notify the user about the scraper process
    print(f"Парсер запущен.")
    
    main()

