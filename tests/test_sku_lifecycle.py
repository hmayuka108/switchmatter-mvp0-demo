from pathlib import Path
import sys
import unittest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from switchmatter.bom import new_component
from switchmatter.envelope import empty_envelope, set_value
from switchmatter.persistence import PipelineStore
import switchmatter.streamlit_ui as streamlit_ui
from switchmatter.streamlit_ui import create_sku, load_sku


class SKULifecycleTests(unittest.TestCase):
    def setUp(self):
        self.store_path = ROOT / "tests" / ".sku_lifecycle_test.json"
        self.store_path.unlink(missing_ok=True)
        self.store_path.with_suffix(".json.tmp").unlink(missing_ok=True)
        self.store = PipelineStore(self.store_path)
        self.original_store = streamlit_ui.STORE
        streamlit_ui.STORE = self.store
        self.state = {"verdict": {"verdict": "HOLD"}, "components": [{"sku_id": "OLD"}]}

    def tearDown(self):
        self.store_path.unlink(missing_ok=True)
        self.store_path.with_suffix(".json.tmp").unlink(missing_ok=True)
        streamlit_ui.STORE = self.original_store

    def app(self):
        return AppTest.from_file(ROOT / "app.py", default_timeout=10).run()

    def test_create_sku_persists_and_activates_empty_envelope(self):
        envelope = create_sku(self.store, self.state, "  SKU-NEW  ")

        self.assertEqual(envelope["sku_id"], "SKU-NEW")
        self.assertEqual(self.state["active_sku"], "SKU-NEW")
        self.assertEqual(self.state["components"], [])
        self.assertNotIn("verdict", self.state)
        self.assertIn("SKU-NEW", self.store.load()["envelopes"])

    def test_blank_and_duplicate_sku_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Enter a New SKU ID"):
            create_sku(self.store, self.state, "  ")
        create_sku(self.store, self.state, "SKU-1")
        with self.assertRaisesRegex(ValueError, "already exists"):
            create_sku(self.store, self.state, "SKU-1")

    def test_selecting_saved_sku_loads_only_its_envelope_and_components(self):
        first, second = empty_envelope("SKU-A"), empty_envelope("SKU-B")
        set_value(first, "pack_format", "bottle", status="confirmed")
        set_value(second, "pack_format", "pouch", status="confirmed")
        self.store.save_envelope(first)
        self.store.save_envelope(second)
        component_a = new_component("SKU-A", "closure", "A-CAP")
        component_b = new_component("SKU-B", "label", "B-LABEL")
        self.store.save_components("SKU-A", [component_a])
        self.store.save_components("SKU-B", [component_b])

        loaded = load_sku(self.store, self.state, "SKU-B")

        self.assertEqual(loaded["values"]["pack_format"]["value"], "pouch")
        self.assertEqual(self.state["active_sku"], "SKU-B")
        self.assertEqual([item["component_id"] for item in self.state["components"]], ["B-LABEL"])
        self.assertNotIn("verdict", self.state)

    def test_selecting_missing_sku_fails_without_changing_active_sku(self):
        self.state["active_sku"] = "KEEP-ME"
        with self.assertRaises(KeyError):
            load_sku(self.store, self.state, "DOES-NOT-EXIST")
        self.assertEqual(self.state["active_sku"], "KEEP-ME")

    def test_streamlit_create_button_clears_input_and_opens_step_zero(self):
        app = self.app()
        app.text_input(key="new_sku_id").input("SKU-WIDGET").run()

        next(button for button in app.button if button.label == "Create SKU").click().run()

        self.assertEqual(list(app.exception), [])
        self.assertEqual(app.text_input(key="new_sku_id").value, "")
        self.assertIn("Step 0 Functional Envelope", [header.value for header in app.header])
        self.assertIn("SKU-WIDGET", self.store.load()["envelopes"])

    def test_streamlit_saved_selection_and_reset_callbacks_are_lifecycle_safe(self):
        self.store.save_envelope(empty_envelope("SKU-A"))
        self.store.save_envelope(empty_envelope("SKU-B"))
        app = self.app()

        app.selectbox(key="sku_selector").select("SKU-B").run()
        self.assertEqual(list(app.exception), [])
        self.assertTrue(any("SKU-B" in item.value for item in app.markdown))

        next(button for button in app.button if button.label == "Start new analysis").click().run()
        self.assertEqual(list(app.exception), [])
        self.assertIn("Start a packaging compliance analysis", [header.value for header in app.header])

    def test_streamlit_duplicate_creation_preserves_saved_data(self):
        self.store.save_envelope(empty_envelope("SKU-EXISTS"))
        app = self.app()
        app.text_input(key="new_sku_id").input("SKU-EXISTS").run()

        next(button for button in app.button if button.label == "Create SKU").click().run()

        self.assertEqual(list(app.exception), [])
        self.assertTrue(any("already exists" in error.value for error in app.error))
        self.assertEqual(list(self.store.load()["envelopes"]), ["SKU-EXISTS"])


if __name__ == "__main__":
    unittest.main()
