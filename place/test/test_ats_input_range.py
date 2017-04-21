"""Test setting various input ranges on an ATS card

This test will not fail if no ATS card is available in the system, it will
simply skip.
"""
from unittest import TestCase, main
from place.alazartech.atsapi import ATS660, ATS9440
from place.alazartech import atsapi as ats

class TestATS(TestCase):
    """Test the ATS card (if available)"""

    def setUp(self):
        try:
            self.board = ats.Board()
        except Exception: #pylint: disable=broad-except
            self.skipTest('No ATS card detected in this machine.')

        # set the capture clock
        # (these values should be supported by all ATS cards)
        self.board.setCaptureClock(
            ats.INTERNAL_CLOCK,
            ats.SAMPLE_RATE_1MSPS,
            ats.CLOCK_EDGE_RISING,
            0
            )

        if self.board.type == ATS660:
            self.range_impedance_tests = [
                # supported modes on ATS660
                (ats.INPUT_RANGE_PM_200_MV, ats.IMPEDANCE_1M_OHM),
                (ats.INPUT_RANGE_PM_200_MV, ats.IMPEDANCE_50_OHM),
                (ats.INPUT_RANGE_PM_400_MV, ats.IMPEDANCE_1M_OHM),
                (ats.INPUT_RANGE_PM_400_MV, ats.IMPEDANCE_50_OHM),
                (ats.INPUT_RANGE_PM_800_MV, ats.IMPEDANCE_1M_OHM),
                (ats.INPUT_RANGE_PM_800_MV, ats.IMPEDANCE_50_OHM),
                (ats.INPUT_RANGE_PM_2_V, ats.IMPEDANCE_1M_OHM),
                (ats.INPUT_RANGE_PM_2_V, ats.IMPEDANCE_50_OHM),
                (ats.INPUT_RANGE_PM_4_V, ats.IMPEDANCE_1M_OHM),
                (ats.INPUT_RANGE_PM_4_V, ats.IMPEDANCE_50_OHM),
                (ats.INPUT_RANGE_PM_8_V, ats.IMPEDANCE_1M_OHM),
                (ats.INPUT_RANGE_PM_8_V, ats.IMPEDANCE_50_OHM),
                (ats.INPUT_RANGE_PM_16_V, ats.IMPEDANCE_1M_OHM),
                (ats.INPUT_RANGE_PM_16_V, ats.IMPEDANCE_50_OHM),
                ]

        elif self.board.type == ATS9440:
            self.range_impedance_tests = [
                # supported modes on ATS9440
                (ats.INPUT_RANGE_PM_100_MV, ats.IMPEDANCE_50_OHM),
                (ats.INPUT_RANGE_PM_200_MV, ats.IMPEDANCE_50_OHM),
                (ats.INPUT_RANGE_PM_400_MV, ats.IMPEDANCE_50_OHM),
                (ats.INPUT_RANGE_PM_1_V, ats.IMPEDANCE_50_OHM),
                (ats.INPUT_RANGE_PM_2_V, ats.IMPEDANCE_50_OHM),
                (ats.INPUT_RANGE_PM_4_V, ats.IMPEDANCE_50_OHM),
                ]

        else:
            self.skipTest('No range/impedance tests found for this card.')

    def test_input_range(self):
        """Test available input ranges and impedance values."""
        for input_range, impedance in self.range_impedance_tests:
            try:
                self.board.inputControl(
                    ats.CHANNEL_A,
                    ats.AC_COUPLING,
                    input_range,
                    impedance
                    )
            except Exception as err: # pylint: disable=broad-except
                self.fail(str(err))

if __name__ == '__main__':
    main(verbosity=2, buffer=True)
