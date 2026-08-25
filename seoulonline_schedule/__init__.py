"""서울온라인학교 참여학교 학사일정 조회 패키지"""

from .schedule import get_schedule, get_schedules_for_all_schools
from .schools import SCHOOLS

__all__ = ["get_schedule", "get_schedules_for_all_schools", "SCHOOLS"]
