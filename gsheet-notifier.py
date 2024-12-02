import time
import gspread
import smtplib
import yaml
from oauth2client.service_account import ServiceAccountCredentials
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# 구글 시트 및 이메일 설정
SHEET_ID = os.getenv('SHEET_ID')
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')
EMAIL_CREDENTIALS_FILE = os.getenv('EMAIL_CREDENTIALS_FILE')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')

# 이메일 정보 로드
def load_email_credentials():
    with open(EMAIL_CREDENTIALS_FILE, 'r') as file:
        credentials = yaml.safe_load(file)
        return credentials['email'], credentials['pw']

EMAIL_ADDRESS, EMAIL_PASSWORD = load_email_credentials()

# 서비스 계정 인증 및 구글 시트 API 접근
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(credentials)

# 이전 데이터 상태 저장
def get_latest_sheet():
    spreadsheet = client.open_by_key(SHEET_ID)
    worksheets = spreadsheet.worksheets()
    latest_sheet = sorted(worksheets, key=lambda ws: ws.title, reverse=True)[0]
    return latest_sheet

sheet = get_latest_sheet()
previous_data = sheet.get_all_values()

# 기존 시트에서의 변화 추적
def get_new_rows(old_data, new_data):
    new_rows = []
    for new_row in new_data:
        if new_row not in old_data:
            new_rows.append(new_row)
    return new_rows

def format_new_rows(new_rows):
    formatted_rows = []
    for row in new_rows:
        # 공백이 아닌 값만 선택하여 포맷팅
        if len(row) >= 4 and row[0] and row[2] and row[3]:
            # 시간 범위와 관련된 데이터 포맷팅
            formatted_row = f"{row[0]}~{row[2]}, {row[3]}"
        else:
            formatted_row = ", ".join([cell for cell in row if cell.strip() != ""])
        if formatted_row:
            formatted_rows.append(formatted_row)
    return formatted_rows

def check_for_updates():
    global previous_data, sheet
    latest_sheet = get_latest_sheet()
    if latest_sheet.title != sheet.title:
        # print(f"💬 새로운 구글 시트가 감지되었습니다: {latest_sheet.title}")
        send_notification_new_sheet(latest_sheet.title)
        sheet = latest_sheet
        previous_data = sheet.get_all_values()
        return

    # 시트를 강제로 다시 불러와 최신 데이터 확보
    current_data = client.open_by_key(SHEET_ID).worksheet(sheet.title).get_all_values()

    # 이전 데이터가 비어있거나 변경사항이 감지될 경우
    if not previous_data or current_data != previous_data:
        new_rows = get_new_rows(previous_data, current_data)
        if new_rows:
            # print("✅ 변경 사항이 감지되었습니다!")
            formatted_new_rows = format_new_rows(new_rows)
            send_notification(formatted_new_rows)
        previous_data = current_data

# 새로운 시트 알림 발송
def send_notification_new_sheet(sheet_name):
    message = MIMEMultipart()
    message['From'] = EMAIL_ADDRESS
    message['To'] = RECEIVER_EMAIL
    message['Subject'] = "새로운 구글 시트가 추가되었습니다"

    body = f"새로운 구글 시트가 추가되었습니다: {sheet_name}"
    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECEIVER_EMAIL, message.as_string())
        # print("새로운 구글 시트 알림 이메일이 발송되었습니다.")
    except Exception as e:
        print(f"이메일 발송 중 오류가 발생했습니다: {e}")

# 변경된 내용 알림 발송
def send_notification(new_data):
    message = MIMEMultipart()
    message['From'] = EMAIL_ADDRESS
    message['To'] = RECEIVER_EMAIL
    message['Subject'] = "구글 시트 업데이트 알림"

    body = "구글 시트에 새로운 내용이 추가되었습니다:\n" + "\n".join(map(str, new_data))
    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECEIVER_EMAIL, message.as_string())
        # print("이메일 알림이 발송되었습니다.")
    except Exception as e:
        print(f"이메일 발송 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    try:
        while True:
            check_for_updates()
            time.sleep(10)  # 10초 간격으로 업데이트 확인
    except KeyboardInterrupt:
        print("프로그램이 종료되었습니다.")
