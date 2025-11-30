import os
import sys
from datetime import datetime
from unittest import TestCase

# Add kimai directory to path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../kimai")))

from kimai.common.common import CommonModule
from kimai.models.timesheet import KimaiTimesheetCollection


class TestCommonModule(TestCase):
    def test_available_time_in_day_single_timesheet_middle(self):
        # Test case: Single timesheet in the middle of the day
        # Expectation: ranges before and after
        date = datetime(2024, 1, 1)
        ts = KimaiTimesheetCollection(
            id=1,
            begin=datetime(2024, 1, 1, 10, 0),
            end=datetime(2024, 1, 1, 11, 0),
            activity=1,
            project=1,
            description="test",
            tags=[],
            user=1,
            exported=False,
            billable=False,
        )

        ranges = CommonModule.available_time_in_day(date, [ts])

        # Current code suspected behavior:
        # first_begin = 10:00
        # start_of_day = 00:00
        # ranges = [(00:00, 10:00)]
        # first_end (11:00) < end_of_day (23:59)
        # append((end, end_of_day)) -> 'end' variable is 10:00!
        # Result: [(00:00, 10:00), (10:00, 23:59)] -> Ignores the task duration!

        print(f"Ranges found: {ranges}")

        self.assertEqual(len(ranges), 2)
        self.assertEqual(ranges[0][0].hour, 0)
        self.assertEqual(ranges[0][1].hour, 10)

        # This assertion fails if the bug exists
        self.assertEqual(ranges[1][0].hour, 11)
        self.assertEqual(ranges[1][1].hour, 23)

    def test_available_time_in_day_multiple_timesheets(self):
        # Test case: Two timesheets with gap
        date = datetime(2024, 1, 1)
        ts1 = KimaiTimesheetCollection(
            id=1,
            begin=datetime(2024, 1, 1, 9, 0),
            end=datetime(2024, 1, 1, 10, 0),
            activity=1,
            project=1,
            description="t1",
            tags=[],
            user=1,
            exported=False,
            billable=False,
        )
        ts2 = KimaiTimesheetCollection(
            id=2,
            begin=datetime(2024, 1, 1, 11, 0),
            end=datetime(2024, 1, 1, 12, 0),
            activity=1,
            project=1,
            description="t2",
            tags=[],
            user=1,
            exported=False,
            billable=False,
        )

        ranges = CommonModule.available_time_in_day(date, [ts1, ts2])

        # Expected: (00-09), (10-11), (12-23:59)

        # If logic is broken for n=2 loop (range(1,1) empty)
        # It might only return first gap and last gap?
        # Or worse.

        # Let's check expectation
        self.assertTrue(
            any(r[0].hour == 10 and r[1].hour == 11 for r in ranges),
            "Gap between tasks missing",
        )


if __name__ == "__main__":
    import unittest

    unittest.main()
