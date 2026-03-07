# SPDX-License-Identifier: GPL-3.0-or-later WITH GPL-3.0-linking-exception
import sys

import pytest

from deluge.pluginmanagerbase import PluginManagerBase


def test_parse_pkg_info_metadata_1_x_no_description():
    """Metadata 1.x has no body fallback; Description must be empty string."""
    pkg_info = 'Metadata-Version: 1.0\nName: Foo\nVersion: 0.1\n'
    info = PluginManagerBase.parse_pkg_info(pkg_info)
    assert info['Description'] == ''


def test_parse_pkg_info_metadata_2_1():
    pkg_info = """Metadata-Version: 2.1
Name: AutoAdd
Version: 1.8
Summary: Monitors folders for .torrent files.
Home-page: http://dev.deluge-torrent.org/wiki/Plugins/AutoAdd
Author: Chase Sterling, Pedro Algarvio
Author-email: chase.sterling@gmail.com, pedro@algarvio.me
License: GPLv3
Platform: UNKNOWN

Monitors folders for .torrent files.
    """
    plugin_info = PluginManagerBase.parse_pkg_info(pkg_info)
    for value in plugin_info.values():
        assert value != ''
    result = 'Monitors folders for .torrent files.'
    assert plugin_info['Description'] == result


def test_scan_finds_specific_builtin_plugins(builtin_egg_info_dir):
    """Well-known built-in plugins must all be present."""
    expected = [
        'AutoAdd',
        'Blocklist',
        'Execute',
        'Extractor',
        'Label',
        'Notifications',
        'Scheduler',
        'Stats',
        'Toggle',
        'WebUi',
    ]
    pm = PluginManagerBase(
        'core.conf', 'deluge.plugin.core', plugin_dirs=[builtin_egg_info_dir]
    )
    assert sorted(pm.available_plugins) == expected


def test_plugin_info_all_values_are_strings(builtin_egg_info_dir):
    """All values from get_plugin_info must be strings, with Name and Version always set."""
    pm = PluginManagerBase(
        'core.conf', 'deluge.plugin.core', plugin_dirs=[builtin_egg_info_dir]
    )
    for plugin in pm.available_plugins:
        info = pm.get_plugin_info(plugin)
        for key, value in info.items():
            assert isinstance(key, str), f'{plugin}: key {key!r} is not str'
            assert isinstance(value, str), f'{plugin}: value for {key!r} is not str'
        assert info['Name'], f'{plugin}: Name is empty'
        assert info['Version'], f'{plugin}: Version is empty'


def test_plugin_info_invalid_name():
    """get_plugin_info for unknown plugin returns sentinel values."""
    pm = PluginManagerBase('core.conf', 'deluge.plugin.core', plugin_dirs=[])
    info = pm.get_plugin_info('NonExistentPlugin')
    assert info['Name'] == 'not available'
    assert info['Version'] == 'not available'


def test_scan_egg_zip(fake_egg):
    """A minimal .egg zip dropped in the plugins dir must be discovered."""
    plugins_dir, _ = fake_egg
    pm = PluginManagerBase('core.conf', 'deluge.plugin.core', plugin_dirs=[plugins_dir])
    assert 'FakePlugin' in pm.available_plugins


def test_scan_egg_link(tmp_path):
    """A .egg-link file pointing at a source dir must be discovered."""
    source_dir = tmp_path / 'MyPlugin'
    egg_info_dir = source_dir / 'MyPlugin.egg-info'
    egg_info_dir.mkdir(parents=True)
    (egg_info_dir / 'PKG-INFO').write_text(
        'Metadata-Version: 1.0\nName: MyPlugin\nVersion: 0.1\n'
    )
    (egg_info_dir / 'entry_points.txt').write_text(
        '[deluge.plugin.core]\nMyPlugin = my_plugin:CorePlugin\n'
    )

    plugins_dir = tmp_path / 'plugins'
    plugins_dir.mkdir()
    (plugins_dir / 'MyPlugin.egg-link').write_text(str(source_dir) + '\n.\n')

    pm = PluginManagerBase('core.conf', 'deluge.plugin.core', plugin_dirs=[plugins_dir])
    assert 'MyPlugin' in pm.available_plugins
    assert pm.get_plugin_info('MyPlugin')['Version'] == '0.1'


@pytest.mark.skipif(
    sys.platform == 'win32',
    reason='pkg_resources normalizes project_name to lowercase on Windows for directory eggs',
)
def test_scan_unpacked_egg_dir(tmp_path):
    """An unpacked .egg directory (Ubuntu-style) with EGG-INFO/ must be discovered."""
    plugins_dir = tmp_path / 'plugins'
    plugins_dir.mkdir()
    egg_dir = plugins_dir / 'FakePlugin-0.1-py3.egg'
    egg_info = egg_dir / 'EGG-INFO'
    egg_info.mkdir(parents=True)
    (egg_info / 'PKG-INFO').write_text(
        'Metadata-Version: 1.0\nName: FakePlugin\nVersion: 0.1\n'
    )
    (egg_info / 'entry_points.txt').write_text(
        '[deluge.plugin.core]\nFakePlugin = fake_plugin:CorePlugin\n'
    )

    pm = PluginManagerBase('core.conf', 'deluge.plugin.core', plugin_dirs=[plugins_dir])
    assert 'FakePlugin' in pm.available_plugins
    assert pm.get_plugin_info('FakePlugin')['Version'] == '0.1'


def test_scan_egg_zip_plugin_info(fake_egg):
    """get_plugin_info returns correct metadata read from EGG-INFO/PKG-INFO inside a zip egg."""
    plugins_dir, _ = fake_egg
    pm = PluginManagerBase('core.conf', 'deluge.plugin.core', plugin_dirs=[plugins_dir])
    info = pm.get_plugin_info('FakePlugin')
    assert info['Name'] == 'FakePlugin'
    assert info['Version'] == '0.1'


def test_no_duplicate_plugins(fake_egg):
    """The same plugin discovered in multiple scan dirs must appear only once."""
    plugins_dir, _ = fake_egg
    # Pass the same dir twice to simulate the plugin appearing in multiple scan paths
    pm = PluginManagerBase(
        'core.conf', 'deluge.plugin.core', plugin_dirs=[plugins_dir, plugins_dir]
    )
    names = [n for n in pm.available_plugins if n == 'FakePlugin']
    assert len(names) == 1
