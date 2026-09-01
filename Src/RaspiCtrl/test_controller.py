import unittest

from controller import ClimateController, ControlConfig


class ClimateControllerTest(unittest.TestCase):
    def setUp(self):
        self.controller = ClimateController(ControlConfig(passive_delay_seconds=10.0))

    def test_normalbetrieb_schaltet_heizen_und_kuehlen_aus(self):
        state = self.controller.update(22.0, 200.0, 0.0)
        self.assertFalse(state.heating)
        self.assertFalse(state.cooling)

    def test_bei_hitze_und_sonne_zuerst_store_schliessen(self):
        state = self.controller.update(25.0, 200.0, 0.0)
        self.assertEqual("closed", state.blind)
        self.assertFalse(state.cooling)
        state = self.controller.update(25.0, 200.0, 10.0)
        self.assertTrue(state.cooling)

    def test_bei_kaelte_und_tageslicht_zuerst_store_oeffnen(self):
        state = self.controller.update(18.0, 200.0, 0.0)
        self.assertEqual("open", state.blind)
        self.assertFalse(state.heating)
        state = self.controller.update(18.0, 200.0, 10.0)
        self.assertTrue(state.heating)

    def test_ohne_tageslicht_sofort_heizen(self):
        state = self.controller.update(18.0, 20.0, 0.0)
        self.assertTrue(state.heating)

    def test_heizen_und_kuehlen_sind_nie_gleichzeitig_aktiv(self):
        states = [
            self.controller.update(30.0, 0.0, 0.0),
            self.controller.update(10.0, 0.0, 1.0),
            self.controller.update(22.0, 0.0, 2.0),
        ]
        self.assertTrue(all(not (state.heating and state.cooling) for state in states))


if __name__ == "__main__":
    unittest.main()
