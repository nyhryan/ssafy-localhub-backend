# LocalHub Backend

## How to run

### Step 1. 개발 환경 구성

```console
$ python -m venv .venv
$ .venv/Scripts/Activate.ps1
$ python -m pip install --upgrade pip
$ echo "*" > .venv/.gitignore
$ pip install -r requirements.txt
$ fastapi dev
$ python -m app/scripts/import_data.py
```

> 사용 중인 환경에 따라 활성화 명령이 다릅니다.
> - Linux, macOS: `source .venv/bin/activate`
> - Windows PowerShell: `.venv/Scripts/Activate.ps1`
> - Windows Git Bash: `source .venv/Scripts/activate`

**1, 2\. 가장 먼저 파이썬 가상 환경을 생성하고 활성화**합니다.

```console
$ which python
/home/user/code/awesome-project/.venv/bin/python

$ Get-Command python
C:\Users\user\code\awesome-project\.venv\Scripts\python
```

가상 환경이 잘 활성화되었는지 위의 명령어(상: Bash/하: PowerShell)로 테스트 할 수 있습니다.

3\. `pip`을 업그레이드합니다.

> `pip`을 업그레이드하는 중 `No module named pip` 오류가 발생한다면 `python -m ensurepip --upgrade`을 실행하고 다시 시도해 봅니다.

4\. 생성한 가상 환경 폴더에 `*`만 적힌 `.gitignore` 파일을 추가합니다.

5\. 프로젝트에 필요한 패키지들을 설치합니다.

6\. 이후 `fastapi dev`로 개발 환경에서 서버를 실행합니다.

7-1\. FastAPI 애플리케이션이 성공적으로 구동되었다면 <kbd>Ctrl+c</kbd>를 눌러 종료합니다.
이후 프로젝트 디렉터리에 `database.db` 파일이 생성되었는지 확인합니다.

7-2\. `python -m app/scripts/import_data` 명령어를 실행하여 데이터베이스에 JSON 공공 데이터를 삽입합니다.
