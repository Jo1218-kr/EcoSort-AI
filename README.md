# ♻️ EcoSort AI (MVP)

카메라를 물건에 비추면 **QR 스캐너처럼 자동으로** 인식해서 한국 기준 **분리배출 방법**을 알려주는 웹앱입니다.

- **UI**: Python + Gradio (갤럭시/안드로이드 Chrome에서 사용)
- **AI**: OpenAI **Responses API** (이미지 입력 + JSON Schema 구조화 출력)
- **자동 인식**: 흑백 프레임 해시와 축소 RGB 색상 차이로 움직임을 감지 → 물건이 1~2초 고정되면 자동 호출 → 같은 장면은 재호출 안 함
- **API 호출 제한**: 세션별 최소 간격 · 전체 합산 간격 · 세션 최대 호출 수 · 일일 한도. 자동 스캔과 사진 탭은 호출 예산을 공유하며, 초기화 버튼은 호출 횟수와 대기 시간을 유지합니다.

## 빠른 시작 — Windows / VS Code

1. Python을 설치합니다. 설치할 때 `Add python.exe to PATH`를 체크합니다.
2. GitHub의 **Code → Download ZIP**으로 내려받고 압축을 풉니다.
3. VS Code에서 `app.py`가 들어 있는 폴더를 엽니다.
4. **터미널 → 새 터미널**을 열고 패키지를 설치합니다.

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. `app.py` 상단의 다음 따옴표 안에 자신의 OpenAI API 키를 입력하고 저장합니다.

   ```python
   OPENAI_API_KEY = ""
   ```

   실제 키를 넣은 파일은 GitHub에 다시 올리지 마세요.
   API 이용에는 별도 사용 요금이 발생할 수 있습니다.

6. 터미널에서 실행합니다.

   ```powershell
   python app.py --share
   ```

7. `Running on public URL` 옆의 HTTPS 주소를 휴대폰에서 엽니다.
8. 먼저 사진 업로드로 분석을 확인한 뒤 자동 스캔을 사용합니다.

PC와 실행 중인 터미널을 유지해야 합니다.
휴대폰에서는 `localhost`나 `0.0.0.0` 대신 공개 HTTPS 주소로 접속하세요.

API 키 없이 화면만 확인하려면 같은 폴더에 `.env` 파일을 만들고
`ECOSORT_MOCK=1`을 입력한 뒤 실행하세요.
이 모드는 실제 인식 대신 고정된 페트병 예제를 표시합니다.
## 1. 설치

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate   /   Windows: .venv\Scripts\activate
pip install -r requirements.txt
# app.py 상단 OPENAI_API_KEY = "" 안에 본인의 키 입력
# .env 는 모델·호출 제한·로그인 설정용 (API 키는 읽지 않음)
```

### API 키를 코드에 직접 입력

`app.py` 상단에 다음 입력란이 있습니다. 실제 키는 제공 파일에 포함되어 있지 않습니다.

```python
OPENAI_API_KEY = ""  # 본인 PC에서만 실제 키 입력
```

입력 후 저장하고 서버를 다시 실행하세요. API 키는 `.env`나 OS 환경변수에서 읽지 않습니다. 나머지 설정은 기존처럼 `.env`에서 읽습니다.

다른 학생들은 본인 PC에서 실행한 HTTPS 주소로 접속해 체험하면 됩니다. 학생 PC에 키를 설정할 필요가 없습니다. 이때 모든 API 비용은 서버 운영자의 키로 발생합니다. `ECOSORT_PASSWORD`를 설정하고 필요한 학생에게만 링크와 로그인 정보를 전달하세요.

**실제 키를 넣은 app.py를 제출하거나 GitHub/단체 채팅에 올리지 마세요.** 제출본은 `OPENAI_API_KEY = ""`로 비우고, 실제 키가 있는 실행본은 본인 PC에만 두세요. 실수로 공개했다면 해당 키를 폐기하고 새로 발급하세요. 본 ZIP에는 실제 키가 없습니다.

> API 키 없이 화면만 먼저 확인하려면 `.env`에 `ECOSORT_MOCK=1` 을 넣으세요.

## 2. 실행 — 갤럭시에서 카메라 쓰기 (HTTPS 필수)

브라우저는 **HTTPS(또는 localhost)** 에서만 카메라를 허용합니다. 가장 쉬운 방법부터:

### 방법 A. Gradio 공개 링크 (가장 빠름, 추천)
```bash
python app.py --share
```
터미널에 나오는 `https://xxxx.gradio.live` 주소를 갤럭시 Chrome(또는 삼성 인터넷)에서 엽니다. 링크는 약 1주일 유효합니다.

> ⚠️ 링크를 아는 누구나 접속할 수 있고 **내 API 키로 비용이 발생**합니다. `.env`에 `ECOSORT_PASSWORD=비밀번호`를 넣으면 로그인(아이디 `ecosort`)이 요구되고, 호출 제한도 함께 적용됩니다.

### 방법 B. Cloudflare Tunnel / ngrok (다른 HTTPS 연결 방법)
```bash
python app.py                      # http://localhost:7860
cloudflared tunnel --url http://localhost:7860   # 또는: ngrok http 7860
```
출력되는 `https://...` 주소로 접속합니다.

### 방법 C. 자체 서명 인증서 (같은 Wi-Fi, 마지막 수단)
```bash
mkdir certs
openssl req -x509 -newkey rsa:2048 -nodes -days 30 \
  -keyout certs/key.pem -out certs/cert.pem -subj "/CN=ecosort" \
  -addext "subjectAltName=IP:192.168.0.10"      # ← 내 PC의 IP로 변경
python app.py --ssl-cert certs/cert.pem --ssl-key certs/key.pem
```
`https://<PC IP>:7860` 으로 접속. 인증서 경고를 통과해야 하며, **일부 Android Chrome에서는 인증서 경고를 넘겨도 카메라가 차단**될 수 있어요. 그 경우 방법 A/B를 쓰세요.

## 3. 사용법
1. 갤럭시 브라우저에서 주소 접속 → **카메라 권한 허용**
2. **녹화(●) 버튼을 한 번** 눌러 스트리밍 시작 (후면 카메라가 우선 선택됩니다. 전면이면 카메라 선택 메뉴에서 변경)
3. 물건 **하나**를 화면 중앙에 크게, 밝은 곳에서 **1~2초 고정** → 자동 인식
4. 다른 물건을 비추면 자동으로 다시 인식. 안 되면 **🎯 지금 인식** 버튼
5. 자동 스캔이 불안정하면 **🖼️ 사진으로 인식** 탭에서 한 장 촬영/업로드

## 4. 호출 제한 & 자동 인식 설정 (`.env`)

| 변수 | 기본값 | 설명 |
|---|---|---|
| `ECOSORT_MIN_INTERVAL` | 4 | 세션당 API 호출 최소 간격(초) |
| `ECOSORT_GLOBAL_MIN_INTERVAL` | 1 | 전체 사용자 합산 최소 간격(초) |
| `ECOSORT_MAX_CALLS_PER_SESSION` | 40 | 한 접속당 최대 호출 수 |
| `ECOSORT_DAILY_LIMIT` | 500 | 서버 하루 총 호출 한도 (재시작 시 초기화) |
| `ECOSORT_STABLE_FRAMES` | 2 | 자동 인식까지 필요한 연속 안정 프레임 수 |
| `ECOSORT_MOVE_THRESH` | 8 | 클수록 손떨림에 관대 (0~64) |
| `ECOSORT_NEW_SCENE_THRESH` | 14 | 클수록 흑백 해시 변화에 덜 민감 |
| `ECOSORT_COLOR_THRESH` | 24 | 축소 RGB 평균 절대 차이 기준(0~255). 낮을수록 색상 변화에 민감 |
| `OPENAI_MODEL` | gpt-4o-mini | 이미지 입력·구조화 출력을 지원하는 모델로 변경 가능 |

자동 인식이 너무 안 되면 `ECOSORT_MOVE_THRESH`를 올리고, 너무 자주 호출되면 `ECOSORT_STABLE_FRAMES`를 올리세요. 색상이 다른 물건으로 바꿔도 인식하지 못하면 `ECOSORT_COLOR_THRESH`를 조금 낮춰 보세요. 조명 변화에도 호출이 발생하면 값을 높여 보세요.

장면 비교는 흑백 해시와 4×4 RGB 배열을 함께 사용합니다. 둘 다 비슷할 때만 같은 장면으로 간주합니다. 실제 물체의 종류나 개체를 추적하는 기능은 아니므로, 비슷한 물건을 놓치거나 조명 변화·손떨림을 새 장면으로 판단할 수 있습니다.

**초기화 동작:** 두 탭의 이미지와 결과, 장면 감지 상태만 초기화합니다. 호출 횟수와 마지막 요청 시각은 유지되어 초기화 직후에도 간격 제한과 최대 40회 한도가 적용됩니다. 자동 스캔과 사진 인식은 같은 세션 상태를 공유합니다. 새로고침·새 접속으로 세션은 새로 만들어질 수 있으며 영구 사용자별 한도는 아닙니다. 서버 전체 일일 한도는 별도로 적용되며 서버 재시작 시 초기화됩니다.

## 5. 구조
```
app.py            화면 및 실행 코드
core.py           이미지 분석 및 분리배출 안내
requirements.txt  설치 패키지 목록
README.md         설치·사용 설명
```

## 6. 한계 (MVP)
- 분리배출 기준은 지자체·아파트마다 다릅니다. 앱에도 안내 문구가 표시됩니다.
- AI 인식은 틀릴 수 있습니다. 기존 `신뢰도 90%` 대신 **관찰 확신: 높음 / 보통 / 낮음**을 표시합니다. 이는 모델이 사진을 보고 생성한 정성적 판단이며 **측정된 정확도나 확률이 아닙니다**. 낮음이면 추가 경고를 표시하고 재질 표시 확인을 요청합니다. 복합 재질은 `부품별 분리`로 안내합니다.
- 호출 카운터(일일 한도)는 메모리 기반이라 서버 재시작 시 초기화됩니다.
- 실제 인식 시 사진은 Gradio 서버를 거쳐 OpenAI API로 전송됩니다. 앱 코드에서 원본 사진을 별도 기록하거나 DB에 저장하지는 않지만, **Gradio 임시 파일과 브라우저 캐시가 생길 수 있습니다**.
- `store=False`는 OpenAI API 응답 저장을 비활성화하는 설정입니다. Gradio 임시 파일 삭제나 공급자 데이터 정책까지 포함한 무보존을 보장하지 않습니다. 얼굴·주소·문서 등 개인정보가 보이지 않도록 물건만 촬영하세요.
- `ECOSORT_MOCK=1`은 고정된 페트병 예제 결과를 보여주는 모드이며 현재 사진을 AI로 인식하지 않습니다.

## 7. 문제 해결
| 증상 | 해결 |
|---|---|
| 카메라가 안 켜짐 | 주소가 `https://`인지 확인, Chrome 사이트 설정에서 카메라 허용 |
| `OPENAI_API_KEY` 경고 | `app.py` 상단 키 입력 후 앱 재시작 |
| 계속 "고정해 주세요" | 폰을 거치하거나 `ECOSORT_MOVE_THRESH`를 12 정도로 상향 |
| 인식 실패: RateLimitError | OpenAI 크레딧/한도 확인 |

## 8. 개선 사항 검증

```bash
python test_core.py
python -m unittest -v test_improvements
```

개선 테스트는 초기화 후 호출 횟수·대기 시간 유지, 한도 도달 후 초기화해도 차단, 두 탭의 상태 공유, 색상만 다른 장면의 재인식, 동일 장면 재호출 생략, 정성적 확신 표시와 JSON 스키마를 확인합니다. API는 모의 응답으로 검증하며 실제 인식 정확도를 측정하지 않습니다. 실제 API 응답과 갤럭시 카메라는 별도로 시연해야 합니다.

이번 변경은 초기화/탭 공유, 색상 감지, 정성적 확신 표시, 사진 저장 안내의 네 가지와 app.py의 API 키 직접 입력을 반영했습니다. 분석·초기화 이벤트는 공통 큐에서 직렬 처리하므로 여러 접속자가 동시에 분석하면 대기 시간이 늘어날 수 있습니다. SDK 재시도 설정과 공유 비밀번호의 선택 설정은 기존과 같습니다.
