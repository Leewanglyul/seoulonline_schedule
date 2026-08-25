"""NEIS OpenAPI를 이용한 학사일정 조회 모듈

NEIS 학사일정 API 명세:
  https://open.neis.go.kr/hub/SchoolSchedule
"""

from __future__ import annotations

import os
from datetime import date, datetime
from typing import Any

import requests

from .schools import OFFICE_CODE, SCHOOLS

NEIS_BASE_URL = "https://open.neis.go.kr/hub/SchoolSchedule"
_DEFAULT_API_KEY = os.environ.get("NEIS_API_KEY", "")


def get_schedule(
    school_code: str,
    from_date: str | date,
    to_date: str | date,
    api_key: str | None = None,
    office_code: str = OFFICE_CODE,
) -> list[dict[str, Any]]:
    """특정 학교의 학사일정을 조회합니다.

    Args:
        school_code: 행정표준코드 (SD_SCHUL_CODE)
        from_date: 조회 시작일 (YYYYMMDD 형식 문자열 또는 date 객체)
        to_date: 조회 종료일 (YYYYMMDD 형식 문자열 또는 date 객체)
        api_key: NEIS API 인증키. None이면 환경변수 NEIS_API_KEY를 사용.
        office_code: 시도교육청코드. 기본값은 서울특별시교육청 코드(B10).

    Returns:
        학사일정 항목 리스트. 각 항목은 API 응답의 row 딕셔너리입니다.

    Raises:
        requests.HTTPError: HTTP 오류 발생 시
        ValueError: API가 오류 코드를 반환할 때
    """
    key = api_key or _DEFAULT_API_KEY
    from_str = _to_date_str(from_date)
    to_str = _to_date_str(to_date)

    params: dict[str, Any] = {
        "Type": "json",
        "pIndex": 1,
        "pSize": 1000,
        "ATPT_OFCDC_SC_CODE": office_code,
        "SD_SCHUL_CODE": school_code,
        "AA_FROM_YMD": from_str,
        "AA_TO_YMD": to_str,
    }
    if key:
        params["KEY"] = key

    response = requests.get(NEIS_BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    # NEIS API 응답 구조: {"SchoolSchedule": [{"head": [...]}, {"row": [...]}]}
    if "SchoolSchedule" not in data:
        # 데이터 없음 (RESULT 오류 코드 INFO-000: 정상, RESULT.CODE == "INFO-200": 데이터 없음)
        result = data.get("RESULT", {})
        code = result.get("CODE", "")
        if code == "INFO-200":
            return []
        raise ValueError(f"NEIS API 오류: {result}")

    schedule_data = data["SchoolSchedule"]
    rows: list[dict[str, Any]] = []
    for item in schedule_data:
        if "row" in item:
            rows.extend(item["row"])
    return rows


def get_schedules_for_all_schools(
    from_date: str | date,
    to_date: str | date,
    api_key: str | None = None,
    schools: list[tuple[str, str]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """서울온라인학교 참여학교 전체의 학사일정을 조회합니다.

    Args:
        from_date: 조회 시작일 (YYYYMMDD 형식 문자열 또는 date 객체)
        to_date: 조회 종료일 (YYYYMMDD 형식 문자열 또는 date 객체)
        api_key: NEIS API 인증키. None이면 환경변수 NEIS_API_KEY를 사용.
        schools: (학교명, SD_SCHUL_CODE) 튜플 목록. None이면 기본 SCHOOLS 목록 사용.

    Returns:
        {학교명: 학사일정 리스트} 형태의 딕셔너리
    """
    if schools is None:
        schools = SCHOOLS

    result: dict[str, list[dict[str, Any]]] = {}
    for school_name, school_code in schools:
        try:
            schedules = get_schedule(
                school_code=school_code,
                from_date=from_date,
                to_date=to_date,
                api_key=api_key,
            )
            result[school_name] = schedules
        except Exception as exc:  # noqa: BLE001
            result[school_name] = [{"error": str(exc)}]
    return result


def _to_date_str(value: str | date) -> str:
    """날짜를 YYYYMMDD 형식 문자열로 변환합니다."""
    if isinstance(value, str):
        # 이미 YYYYMMDD 형식이면 그대로 반환, YYYY-MM-DD 형식이면 변환
        normalized = value.replace("-", "")
        if len(normalized) == 8 and normalized.isdigit():
            return normalized
        raise ValueError(f"날짜 형식이 올바르지 않습니다: {value!r}. YYYYMMDD 또는 YYYY-MM-DD 형식을 사용하세요.")
    if isinstance(value, datetime):
        return value.strftime("%Y%m%d")
    return value.strftime("%Y%m%d")
