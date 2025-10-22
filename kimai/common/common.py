from collections import defaultdict
from datetime import datetime, timedelta
from typing import DefaultDict, Dict, List, Optional, cast

from kimai.models.timesheet import KimaiTimesheetCollection
from kimai.services.kimai.kimai import KimaiService

kimai_service = KimaiService.get_instance()

class CommonModule:
  @classmethod
  def timesheets_per_day(cls, begin: datetime, end: Optional[datetime] = None) -> Dict[str, List[KimaiTimesheetCollection]]:
    """
    Returns the available timeseehts divided by day in a specified time range.

    @params
    begin[datetime]: The start of the range.
    end[Optional[datetime]]: The end of the range. When argument is not provided
    it defaults to the end of de begin date.

    @return
    Dict[str, List[KimaiTimesheetCollection]]: A dictionary consisting of each day
    in the range with its corresponding list of timesheets.
    """
    begin = begin.replace(hour = 0, minute = 0)

    if(not end): end = begin.replace(hour = 23, minute = 59)
    else: end = end.replace(hour = 23, minute = 59)

    timesheets_in_range = kimai_service.get_timesheets({
      "begin": begin.isoformat(),
      "end": end.isoformat()
    })

    timesheets_by_day = DefaultDict(list)
    for day in range((end - begin).days):
      begin_date = (begin + timedelta(days = day)).strftime("%Y%m%d")
      timesheets_by_day[begin_date] = []

    for timesheet in timesheets_in_range:
      begin_date = timesheet.begin.strftime("%Y%m%d")
      end_date = timesheet.end.strftime("%Y%m%d")

      if(begin_date != end_date):
        current_day_timesheet = timesheet.model_copy()
        current_day_timesheet.end = timesheet.end.replace(hour = 23, minute = 59)

        next_day_timesheet = timesheet.model_copy()
        next_day_timesheet.begin = timesheet.end.replace(hour = 0, minute = 0)

        timesheets_by_day[end_date].append(next_day_timesheet)
        timesheets_by_day[begin_date].append(current_day_timesheet)
      else:
        timesheets_by_day[begin_date].append(timesheet)

    return timesheets_by_day

  @classmethod
  def available_time_in_day(cls, date: datetime, timesheets: List[KimaiTimesheetCollection]) -> List[tuple[datetime, datetime]]:
    """
    Returns the available time ranges in a day according to its timesheets.

    @params
    date[datetime]: The day in question.
    timesheets[List[KimaiTimesheetCollection]]: The list of timesheets of the day.
    it defaults to the end of de begin date.

    @return
    Dict[str, List[KimaiTimesheetCollection]]: A dictionary consisting of each day
    in the range with its corresponding list of timesheets.
    """
    timesheets.sort(key = lambda timesheet: timesheet.begin)

    if(not timesheets):
      return [(date, date.replace(hour = 23, minute = 59))]

    n = len(timesheets)

    start_of_day = datetime(day = date.day, month = date.month, year = date.year, hour = 0, minute = 0)
    end_of_day = datetime(day = date.day, month = date.month, year = date.year, hour = 23, minute = 59)

    first_timesheet = timesheets[0]
    first_begin = first_timesheet.begin.replace(tzinfo = None)
    first_end = cast(datetime, first_timesheet.end).replace(tzinfo = None)

    if(n == 1):
      if(first_begin > start_of_day):
        start = start_of_day
        end = first_begin

        ranges = [(start, end)]
        if(first_end < end_of_day):
          ranges.append((end, end_of_day))

        return ranges
      else:
        return [(first_end, end_of_day)]

    start = start_of_day if first_begin >= start_of_day else first_end
    end = first_begin if first_begin >= start_of_day else timesheets[1].begin

    ranges = [(start, end)]

    for i in range(1, n - 1):
      current_timesheet, next_timesheet = timesheets[i], timesheets[i + 1]
      start = cast(datetime, current_timesheet.end).replace(tzinfo = None)
      end = cast(datetime, next_timesheet.begin).replace(tzinfo = None)

      if(start == end): continue

      ranges.append((start, end))

    last_timesheet = timesheets[-1]
    last_end = cast(datetime, last_timesheet.end).replace(tzinfo = None)

    if(last_end < end_of_day):
      start = last_end
      end = end_of_day

      ranges.append((start, end))

    return ranges

  @classmethod
  def available_times_in_range(cls, begin: datetime, end: datetime) -> Dict:
    """
    Returns the available time ranges in a range.

    @params
    begin[datetime]: The start of the range.
    end[datetime]: The end of the range.

    @return
    Dict[str, List[KimaiTimesheetCollection]]: A dictionary consisting of each day
    in the range with its corresponding list of timesheets.
    """
    timesheets = cls.timesheets_per_day(begin, end)
    ranges_by_day = defaultdict()

    for day, timesheet_list in timesheets.items():
      date = datetime.strptime(day, "%Y%m%d")
      available_times = cls.available_time_in_day(date, timesheet_list)

      ranges_by_day[day] = available_times

    return ranges_by_day

