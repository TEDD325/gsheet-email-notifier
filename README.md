# Google Sheet 변경 사항 감지 및 자동 이메일 알람

## 1. Google Cloud API setting 방법
1. GCP 콘솔 -> API 및 서비스(https://console.cloud.google.com/apis/dashboard?hl=ko&project=phrasal-ground-432304-k3)
2. `리소스, 문서, 제품 등 검색` 바에서 `sheet` 검색
3. Google Sheets API `사용/활성화`
4. Google Sheets API의 `사용자 인증 정보`
5. `사용자 인증 정보 만들기`
6. `서비스 계정`
7. 서비스 계정 만들기에서 적절한 서비스 계정 이름 부여: e.g.,`gsheet-notifier`
8. 만들어진 서비스 계정 -> 키 -> 키 추가 -> 새 키 만들기
9. `JSON` 선택 후 `만들기`
10. 해당 키를 적절한 위치에 넣기

## 2. Google App Password 생성 (Gmail 기준)
- https://myaccount.google.com/apppasswords
- PW 복사 (공백 제거)

## 3. 이메일 정보가 담긴 yaml 파일 생성
```yaml
email: [Google App Password에서 앱 비밀번호 생성에 쓰인 계정 입력 e.b., example@gmail.com]
pw: [Google App Password에서 생성한 비밀번호 입력]
```

## 4. [MacOS 기준] `~/.zshrc`에 다음의 내용을 alias로 등록
```sh
export SHEET_ID=구글 시트의 ID
export CREDENTIALS_FILE=[1. Google Cloud API setting 방법]에서 생성한 json 파일의 위치
export EMAIL_CREDENTIALS_FILE=이메일 정보가 담긴 yaml 파일의 경로
export RECEIVER_EMAIL=수신 받고자 하는 이메일 주소
```

## 5. [Optional] `~/.zshrc`에 프로그램 자동 실행 스크립트 추가
```sh
sudo vi ~/.zshrc
```

```sh
# gsheet-noti 환경 활성화 후 스크립트 자동 실행
if [ -n "$PS1" ]; then
    conda activate gsheet-noti 
    python path/gsheet-notifier.py &
fi
```

```sh
source ~/.zshrc
```