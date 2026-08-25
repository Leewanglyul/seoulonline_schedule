# seoulonline_schedule

서울온라인학교 참여학교의 학사일정을 NEIS(나이스) OpenAPI를 이용해 조회하는 Python 패키지입니다.

## 설치

```bash
pip install -e .
```

## 사용법

### 환경 변수 설정

NEIS API 인증키를 환경변수로 설정합니다. ([나이스 교육정보 개방 포털](https://open.neis.go.kr)에서 무료 발급)

```bash
export NEIS_API_KEY=your_api_key_here
```

### CLI 사용

```bash
# 전체 학교 학사일정 조회 (해당 연도)
seoulonline-schedule

# 특정 기간 조회
seoulonline-schedule --from-date 20250301 --to-date 20250630

# 특정 학교만 조회
seoulonline-schedule --school 서울온라인학교

# JSON 형식으로 출력
seoulonline-schedule --output json

# API 키를 직접 전달
seoulonline-schedule --api-key YOUR_KEY
```

### Python API 사용

```python
from seoulonline_schedule import get_schedule, get_schedules_for_all_schools, SCHOOLS

# 특정 학교 학사일정 조회
schedules = get_schedule(
    school_code="9290076",   # 서울온라인학교
    from_date="20250301",
    to_date="20251231",
)

for item in schedules:
    print(item["AA_YMD"], item["EVENT_NM"])

# 전체 참여학교 학사일정 조회
all_schedules = get_schedules_for_all_schools(
    from_date="20250301",
    to_date="20251231",
)

for school_name, items in all_schedules.items():
    print(f"=== {school_name} ===")
    for item in items:
        print(" ", item["AA_YMD"], item["EVENT_NM"])
```

## 참여학교 목록

`seoulonline_schedule.schools.SCHOOLS` 에서 확인할 수 있습니다.

```python
from seoulonline_schedule import SCHOOLS

for name, code in SCHOOLS:
    print(name, code)
```

## 테스트

```bash
pip install pytest
pytest
```

## API 출처

- [나이스 교육정보 개방 포털 - 학사일정](https://open.neis.go.kr/hub/SchoolSchedule)
- 시도교육청코드: `B10` (서울특별시교육청)
