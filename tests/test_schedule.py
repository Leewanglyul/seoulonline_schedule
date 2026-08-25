"""학사일정 조회 모듈 테스트"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from seoulonline_schedule.schedule import _to_date_str, get_schedule
from seoulonline_schedule.schools import OFFICE_CODE, SCHOOLS


def test_schools_list_not_empty():
    assert len(SCHOOLS) > 0


def test_schools_have_correct_format():
    for name, code in SCHOOLS:
        assert isinstance(name, str) and name
        assert isinstance(code, str) and code.isdigit()


def test_office_code():
    assert OFFICE_CODE == "B10"


def test_to_date_str_yyyymmdd():
    assert _to_date_str("20250301") == "20250301"


def test_to_date_str_with_dash():
    assert _to_date_str("2025-03-01") == "20250301"


def test_to_date_str_date_object():
    from datetime import date

    assert _to_date_str(date(2025, 3, 1)) == "20250301"


def test_to_date_str_invalid():
    with pytest.raises(ValueError):
        _to_date_str("2025/03/01")


_SAMPLE_RESPONSE = {
    "SchoolSchedule": [
        {
            "head": [
                {"list_total_count": 1},
                {"RESULT": {"CODE": "INFO-000", "MESSAGE": "정상 처리되었습니다."}},
            ]
        },
        {
            "row": [
                {
                    "ATPT_OFCDC_SC_CODE": "B10",
                    "ATPT_OFCDC_SC_NM": "서울특별시교육청",
                    "SD_SCHUL_CODE": "9290076",
                    "SCHUL_NM": "서울온라인학교",
                    "AY": "2025",
                    "JULD": "1",
                    "MLSV_FROM_YMD": "20250301",
                    "MLSV_TO_YMD": "20250301",
                    "MLSV_NM": "학년도 시업일",
                    "EVENT_NM": "학년도 시업일",
                    "EVENT_CNTNT": "",
                    "ONE_GRADE_EVENT_YN": "Y",
                    "TW_GRADE_EVENT_YN": "Y",
                    "THREE_GRADE_EVENT_YN": "Y",
                    "FR_GRADE_EVENT_YN": "N",
                    "FIV_GRADE_EVENT_YN": "N",
                    "SIX_GRADE_EVENT_YN": "N",
                    "SBTR_DD_SC_NM": "학사일",
                    "AA_YMD": "20250301",
                    "LOAD_DTM": "20250101",
                }
            ]
        },
    ]
}

_EMPTY_RESPONSE = {"RESULT": {"CODE": "INFO-200", "MESSAGE": "해당하는 데이터가 없습니다."}}


@patch("seoulonline_schedule.schedule.requests.get")
def test_get_schedule_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = _SAMPLE_RESPONSE
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    rows = get_schedule(
        school_code="9290076",
        from_date="20250301",
        to_date="20250331",
    )

    assert len(rows) == 1
    assert rows[0]["EVENT_NM"] == "학년도 시업일"
    assert rows[0]["AA_YMD"] == "20250301"


@patch("seoulonline_schedule.schedule.requests.get")
def test_get_schedule_empty(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = _EMPTY_RESPONSE
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    rows = get_schedule(
        school_code="9290076",
        from_date="20250301",
        to_date="20250331",
    )

    assert rows == []


@patch("seoulonline_schedule.schedule.requests.get")
def test_get_schedule_api_error(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"RESULT": {"CODE": "ERROR-300", "MESSAGE": "인증 오류"}}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    with pytest.raises(ValueError, match="NEIS API 오류"):
        get_schedule(
            school_code="9290076",
            from_date="20250301",
            to_date="20250331",
        )


@patch("seoulonline_schedule.schedule.requests.get")
def test_get_schedule_uses_api_key(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = _SAMPLE_RESPONSE
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    get_schedule(
        school_code="9290076",
        from_date="20250301",
        to_date="20250331",
        api_key="test-key",
    )

    call_kwargs = mock_get.call_args
    params = call_kwargs.kwargs.get("params") or call_kwargs.args[1]
    assert params["KEY"] == "test-key"
