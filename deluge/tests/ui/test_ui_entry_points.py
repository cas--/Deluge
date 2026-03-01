# SPDX-License-Identifier: GPL-3.0-or-later WITH GPL-3.0-linking-exception

"""Tests for deluge.ui entry point discovery."""

from deluge.ui.ui_entry import get_ui_entrypoints


def test_deluge_ui_entry_point_names():
    """Expected UI names must be registered as entry points."""
    assert sorted(get_ui_entrypoints()) == ['console', 'gtk', 'web']


def test_deluge_ui_entry_points_loadable():
    """All discovered deluge.ui entry points must return a non-None class."""
    for cls in get_ui_entrypoints().values():
        assert cls is not None
