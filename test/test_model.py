from math import sqrt
from unittest import TestCase
import time
from unittest.mock import patch
from piscis.model import MovementVector, DEGREES_45, ScalingVector, TimeTracker, PredatorFactory, Predator

STARTING_EPOCH = 100000000
CURRENT_EPOCH = 100001414


# noinspection PyPep8Naming
def assertEqualFloat(actual, expected, error_margin=0.5):  # pragma: no cover
    if not abs(actual - expected) <= error_margin:
        raise AssertionError("Actual: %s\nExpected: %s with range of %s" % (actual, expected, error_margin))


class TimeTrackerTestCase(TestCase):
    def test_start_movement_saves_current_time(self):
        time_tracker = TimeTracker()
        time_tracker.start(STARTING_EPOCH)
        self.assertEqual(time_tracker.starting_epoch, STARTING_EPOCH)

    def test_get_delta(self):
        time_tracker = TimeTracker()
        time_tracker.start(STARTING_EPOCH)
        assertEqualFloat(time_tracker.get_delta(CURRENT_EPOCH), sqrt(2))


class MovementVectorTestCase(TestCase):
    def setUp(self):
        self.velocity = (DEGREES_45, 5)
        self.starting_pos = (5, 5)
        self.mv = MovementVector(self.starting_pos, self.velocity)

    def test_can_step_along_direction_by_velocity(self):
        self.assertEqual(self.mv.starting_position, self.starting_pos)
        self.assertEqual(self.velocity, (self.mv.angle, self.mv.magnitude))

    def test_get_current_position_relative_to_time(self):
        self.mv.start(STARTING_EPOCH)
        assertEqualFloat(self.mv.get_current_position(CURRENT_EPOCH)[0], 10.)
        assertEqualFloat(self.mv.get_current_position(CURRENT_EPOCH)[1], 10.)


class ScalingVectorTestCase(TestCase):
    def setUp(self):
        self.target_diameter = 5
        self.velocity = 50
        self.vector = ScalingVector(self.target_diameter, self.velocity)

    def test_initial_size_is_zero(self):
        assertEqualFloat(self.vector.get_current_diameter(self.vector.starting_epoch), 0.0)

    def test_has_target_size_and_velocity(self):
        self.assertEqual(self.target_diameter, self.vector.target_diameter)

    def test_has_target_size(self):
        self.assertEqual(self.velocity, self.vector.velocity)

    def test_get_current_size_relative_to_time_for_a_big_change(self):
        vector = ScalingVector(500, 1000)
        self.vector.start(0)
        current_diameter = vector.get_current_diameter(100)
        assertEqualFloat(current_diameter, 100)

    def test_when_target_size_is_reached_is_target_size_reached_true(self):
        vector = ScalingVector(500, 1000)
        self.vector.start(0)
        self.assertTrue(vector.is_target_diameter_reached(600))
        self.assertFalse(vector.is_target_diameter_reached(100))


class PredatorTestCase(TestCase):
    def setUp(self):
        self.starting_epoch = int(time.time()*1000)
        self.starting_position = (5, 5)
        self.target_diameter = 120
        self.scaling_velocity = 5
        sv = ScalingVector(self.target_diameter, self.scaling_velocity)
        mv = MovementVector(self.starting_position, (0, 0))
        self.pr = Predator("#FF0000", mv, sv)
        self.pr.start_both(self.starting_epoch)

    def test_has_color(self):
        self.assertEqual(self.pr.color, "#FF0000")

    def test_can_start_both(self):
        self.pr.start_both(10)
        self.assertEqual(self.pr.scaling_vector.starting_epoch, 10)
        self.assertEqual(self.pr.movement_vector.starting_epoch, 10)

    def test_can_reset_scaling(self):
        self.pr.reset_scaling(500)
        self.assertEqual(self.pr.scaling_vector.starting_epoch, 500)

    def test_can_ask_for_starting_position(self):
        self.assertEqual(self.starting_position, self.pr.get_starting_position())

    def test_can_set_scaling_velocity(self):
        velocity = 50
        self.pr.set_scaling_velocity(velocity)
        self.assertEqual(velocity, self.pr.scaling_vector.velocity)

    def test_can_set_target_diameter(self):
        target_diameter = 120
        self.pr.set_target_diameter(target_diameter)
        assertEqualFloat(target_diameter, self.pr.scaling_vector.target_diameter)

    @patch("time.time")
    def test_when_target_diameter_is_reached_restart_scaling(self, mock_time):
        mock_time.return_value = 50
        self.pr.start_scaling(time.time())
        mock_time.return_value = 120

        self.pr.get_current_diameter(100)
        assertEqualFloat(self.pr.scaling_vector.starting_epoch, 50)

    @patch("time.time")
    def test_when_target_diamater_is_not_reached_keep_scaling_up(self, mock_time):
        mock_time.return_value = 50
        self.pr.start_scaling(time.time())
        mock_time.return_value = 120

        self.pr.get_current_diameter(400000)
        assertEqualFloat(self.pr.scaling_vector.starting_epoch, 120000.)

    def test_old_diameter_accessors(self):
        self.pr.set_old_diameter(5)
        self.assertEqual(self.pr.get_old_diameter(), 5)

    def test_target_diameter_accessors(self):
        self.assertEqual(self.pr.get_target_diameter(), 120)


class PredatorFactoryTestCase(TestCase):
    def setUp(self):
        self.pf = PredatorFactory()

    def test_sets_predator_starting_position(self):
        self.pf.starting_position = (5, 5)
        self.assertEqual(self.pf.create().movement_vector.starting_position, (5, 5))

    def test_sets_predator_movement_velocity(self):
        self.pf.movement_velocity = (45, 5)
        self.assertEqual(self.pf.create().movement_vector.angle, 45)
        self.assertEqual(self.pf.create().movement_vector.magnitude, 5)

    def test_sets_predator_scaling_velocity(self):
        self.pf.scaling_velocity = 10
        self.assertEqual(self.pf.create().scaling_vector.velocity, 10)

    def test_sets_predator_target_diameter(self):
        self.pf.target_diameter = 500
        self.assertEqual(self.pf.create().scaling_vector.target_diameter, 500)

    def test_sets_predator_color(self):
        self.pf.color = "#FF00FF"
        self.assertEqual(self.pf.create().color, "#FF00FF")
