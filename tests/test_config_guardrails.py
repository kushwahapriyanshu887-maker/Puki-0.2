import json
import tempfile
import unittest
from pathlib import Path

from config import get_config
from core.llm_client import _load_config
from memory import config_manager


class ConfigGuardrailsTests(unittest.TestCase):
    def test_load_api_keys_rejects_non_dict_payload(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = Path(td) / "api_keys.json"
            cfg.write_text('["bad", "config"]', encoding="utf-8")

            original_dir = config_manager.CONFIG_DIR
            original_file = config_manager.CONFIG_FILE
            try:
                config_manager.CONFIG_DIR = Path(td)
                config_manager.CONFIG_FILE = cfg

                self.assertEqual(config_manager.load_api_keys(), {})
                self.assertTrue(config_manager.get_plugin_enabled("demo_plugin"))

                config_manager.save_api_keys("  gemini-123456  ")
                saved = json.loads(cfg.read_text(encoding="utf-8"))
                self.assertEqual(saved["gemini_api_key"], "gemini-123456")
            finally:
                config_manager.CONFIG_DIR = original_dir
                config_manager.CONFIG_FILE = original_file

    def test_readers_return_empty_dict_when_config_is_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = Path(td) / "api_keys.json"
            cfg.write_text('{"llm_provider": 42}', encoding="utf-8")

            original_cfg_path = __import__("config")._CONFIG_PATH
            original_llm_cfg = __import__("core.llm_client", fromlist=["CONFIG_PATH"]).CONFIG_PATH

            try:
                import config as config_module
                import core.llm_client as llm_client

                config_module._CONFIG_PATH = cfg
                llm_client.CONFIG_PATH = cfg

                self.assertEqual(get_config(), {"llm_provider": 42})
                self.assertEqual(_load_config(), {"llm_provider": 42})
            finally:
                import config as config_module
                import core.llm_client as llm_client

                config_module._CONFIG_PATH = original_cfg_path
                llm_client.CONFIG_PATH = original_llm_cfg


if __name__ == "__main__":
    unittest.main()
