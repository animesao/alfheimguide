import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cogs.help import CATEGORY_COMMANDS, CATEGORIES_RU, CATEGORIES_EN


def test_category_keys_match():
    assert set(CATEGORY_COMMANDS.keys()) == set(CATEGORIES_RU.keys())
    assert set(CATEGORY_COMMANDS.keys()) == set(CATEGORIES_EN.keys())


def test_all_categories_have_commands():
    for key, cmds in CATEGORY_COMMANDS.items():
        assert len(cmds) > 0, f"Category {key} has no commands"


def test_no_duplicate_commands():
    seen = {}
    for key, cmds in CATEGORY_COMMANDS.items():
        for cmd in cmds:
            assert cmd not in seen, f"Command {cmd} in both {seen[cmd]} and {key}"
            seen[cmd] = key


def test_category_labels_unique():
    ru_values = list(CATEGORIES_RU.values())
    en_values = list(CATEGORIES_EN.values())
    assert len(ru_values) == len(set(ru_values)), "Duplicate RU category labels"
    assert len(en_values) == len(set(en_values)), "Duplicate EN category labels"
