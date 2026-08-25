"""서울온라인학교 학사일정 조회 CLI

사용법:
    python -m seoulonline_schedule [--from-date YYYYMMDD] [--to-date YYYYMMDD] [--school 학교명]
"""

from __future__ import annotations

import argparse
import json
from datetime import date

from .schedule import get_schedule, get_schedules_for_all_schools
from .schools import SCHOOLS


def main() -> None:
    parser = argparse.ArgumentParser(
        description="서울온라인학교 참여학교 학사일정 조회"
    )
    today = date.today()
    year = today.year
    parser.add_argument(
        "--from-date",
        default=f"{year}0301",
        help="조회 시작일 (YYYYMMDD, 기본: 해당 연도 3월 1일)",
    )
    parser.add_argument(
        "--to-date",
        default=f"{year}1231",
        help="조회 종료일 (YYYYMMDD, 기본: 해당 연도 12월 31일)",
    )
    parser.add_argument(
        "--school",
        default=None,
        help="특정 학교명 (기본: 전체 학교 조회)",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="NEIS API 인증키 (미입력 시 환경변수 NEIS_API_KEY 사용)",
    )
    parser.add_argument(
        "--output",
        choices=["json", "text"],
        default="text",
        help="출력 형식 (기본: text)",
    )
    args = parser.parse_args()

    if args.school:
        matched = [(name, code) for name, code in SCHOOLS if name == args.school]
        if not matched:
            print(f"학교를 찾을 수 없습니다: {args.school}")
            print("등록된 학교 목록:")
            for name, _ in SCHOOLS:
                print(f"  - {name}")
            return
        school_name, school_code = matched[0]
        schedules = get_schedule(
            school_code=school_code,
            from_date=args.from_date,
            to_date=args.to_date,
            api_key=args.api_key,
        )
        result = {school_name: schedules}
    else:
        result = get_schedules_for_all_schools(
            from_date=args.from_date,
            to_date=args.to_date,
            api_key=args.api_key,
        )

    if args.output == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_text(result)


def _print_text(result: dict) -> None:
    for school_name, schedules in result.items():
        print(f"\n{'='*60}")
        print(f"  {school_name}")
        print(f"{'='*60}")
        if not schedules:
            print("  (학사일정 없음)")
            continue
        for item in schedules:
            if "error" in item:
                print(f"  [오류] {item['error']}")
                continue
            date_str = item.get("AA_YMD", "")
            event = item.get("EVENT_NM", "")
            grade = _grade_str(item)
            print(f"  {date_str}  {event}{grade}")


def _grade_str(item: dict) -> str:
    grade_keys = [
        ("ONE_GRADE_EVENT_YN", "1"),
        ("TW_GRADE_EVENT_YN", "2"),
        ("THREE_GRADE_EVENT_YN", "3"),
        ("FR_GRADE_EVENT_YN", "4"),
        ("FIV_GRADE_EVENT_YN", "5"),
        ("SIX_GRADE_EVENT_YN", "6"),
    ]
    grades = [label for key, label in grade_keys if item.get(key) == "Y"]
    if grades:
        return f" [{','.join(grades)}학년]"
    return ""


if __name__ == "__main__":
    main()
