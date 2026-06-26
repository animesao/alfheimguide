import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import MESSAGES


def test_ru_en_keys_match():
    ru_keys = set(MESSAGES["ru"].keys())
    en_keys = set(MESSAGES["en"].keys())
    only_ru = ru_keys - en_keys
    only_en = en_keys - ru_keys
    assert not only_ru, f"Keys only in RU: {only_ru}"
    assert not only_en, f"Keys only in EN: {only_en}"


def test_all_messages_have_content():
    for lang in ("ru", "en"):
        for key, val in MESSAGES[lang].items():
            assert val, f"Empty message for {lang}.{key}"
