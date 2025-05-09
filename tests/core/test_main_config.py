import configparser
import logging
import unittest
from textwrap import dedent

from b3.config import CfgConfigParser, MainConfig, load
from b3.functions import getAbsolutePath


class CommonDefaultTestMethodsMixin:
    def test_b3_section(self):
        self.assertEqual("changeme", self.conf.get("b3", "parser"))
        self.assertEqual(
            "sqlite:///var/b3/b3_db.sqlite", self.conf.get("b3", "database")
        )
        self.assertEqual("b3", self.conf.get("b3", "bot_name"))
        self.assertEqual("^0(^2b3^0)^7:", self.conf.get("b3", "bot_prefix"))
        self.assertEqual("%I:%M%p %Z %m/%d/%y", self.conf.get("b3", "time_format"))
        self.assertEqual("UTC", self.conf.get("b3", "time_zone"))
        self.assertEqual("20", self.conf.get("b3", "log_level"))
        self.assertEqual("b3.log", self.conf.get("b3", "logfile"))

    def test_server_section(self):
        self.assertEqual("password", self.conf.get("server", "rcon_password"))
        self.assertEqual("27960", self.conf.get("server", "port"))
        self.assertEqual("games_mp.log", self.conf.get("server", "game_log"))
        self.assertEqual("127.0.0.1", self.conf.get("server", "public_ip"))
        self.assertEqual("127.0.0.1", self.conf.get("server", "rcon_ip"))
        self.assertEqual("0.33", self.conf.get("server", "delay"))
        self.assertEqual("50", self.conf.get("server", "lines_per_second"))

    def test_messages_section(self):
        self.assertEqual(
            """$clientname^7 was kicked by $adminname^7 $reason""",
            self.conf.get("messages", "kicked_by"),
        )
        self.assertEqual(
            """$clientname^7 was kicked $reason""", self.conf.get("messages", "kicked")
        )
        self.assertEqual(
            """$clientname^7 was banned by $adminname^7 $reason""",
            self.conf.get("messages", "banned_by"),
        )
        self.assertEqual(
            """$clientname^7 was banned $reason""", self.conf.get("messages", "banned")
        )
        self.assertEqual(
            """$clientname^7 was temp banned by $adminname^7 for $banduration^7 $reason""",
            self.conf.get("messages", "temp_banned_by"),
        )
        self.assertEqual(
            """$clientname^7 was temp banned for $banduration^7 $reason""",
            self.conf.get("messages", "temp_banned"),
        )
        self.assertEqual(
            """$clientname^7 was un-banned by $adminname^7 $reason""",
            self.conf.get("messages", "unbanned_by"),
        )
        self.assertEqual(
            """$clientname^7 was un-banned^7 $reason""",
            self.conf.get("messages", "unbanned"),
        )

    def test_get_external_plugins_dir(self):
        self.assertEqual(
            getAbsolutePath("@b3/extplugins"), self.conf.get_external_plugins_dir()
        )

    def test_get_plugins(self):
        self.assertListEqual(
            [
                {
                    "name": "admin",
                    "conf": "@b3/conf/plugin_admin.ini",
                    "disabled": False,
                    "path": None,
                },
                {
                    "name": "adv",
                    "conf": "@b3/conf/plugin_adv.ini",
                    "disabled": False,
                    "path": None,
                },
                {
                    "name": "poweradminurt",
                    "conf": "@b3/conf/plugin_poweradminurt.ini",
                    "disabled": False,
                    "path": None,
                },
                {
                    "name": "spree",
                    "conf": "@b3/conf/plugin_spree.ini",
                    "disabled": False,
                    "path": None,
                },
                {
                    "name": "stats",
                    "conf": "@b3/conf/plugin_stats.ini",
                    "disabled": False,
                    "path": None,
                },
                {
                    "name": "welcome",
                    "conf": "@b3/conf/plugin_welcome.ini",
                    "disabled": False,
                    "path": None,
                },
                {
                    "name": "knifer",
                    "conf": "@b3/conf/plugin_knifer.ini",
                    "disabled": False,
                    "path": None,
                },
                {
                    "name": "nader",
                    "conf": "@b3/conf/plugin_nader.ini",
                    "disabled": False,
                    "path": None,
                },
                {
                    "name": "booter",
                    "conf": "@b3/conf/plugin_booter.ini",
                    "disabled": False,
                    "path": None,
                },
                {
                    "name": "flagstats",
                    "conf": "@b3/conf/plugin_flagstats.ini",
                    "disabled": False,
                    "path": None,
                },
                {
                    "name": "headshotsurt",
                    "conf": "@b3/conf/plugin_headshotsurt.ini",
                    "disabled": False,
                    "path": None,
                },
            ],
            self.conf.get_plugins(),
        )


class Test_CfgMainConfigParser(CommonDefaultTestMethodsMixin, unittest.TestCase):
    def setUp(self):
        self.conf = MainConfig(load(getAbsolutePath("@b3/conf/b3.distribution.ini")))
        log = logging.getLogger("output")
        log.setLevel(logging.DEBUG)

    def test_plugins_order(self):
        """
        Vefify that the plugins are return in the same order as found in the config file
        """
        self.assertListEqual(
            self.conf._config_parser.options("plugins"),
            [
                "admin",
                "adv",
                "poweradminurt",
                "spree",
                "stats",
                "welcome",
                "knifer",
                "nader",
                "booter",
                "flagstats",
                "headshotsurt",
            ],
        )


class TestConfig(unittest.TestCase):
    def init(self, cfg_content):
        cfg_parser = CfgConfigParser(allow_no_value=True)
        cfg_parser.loadFromString(cfg_content)
        conf_cfg = MainConfig(cfg_parser)

        return conf_cfg

    def test_empty_conf(self):
        self.init("")

    def test_external_dir_missing(self):
        conf_cfg = self.init(
            dedent(
                r"""
            [b3]
        """
            )
        )
        # normalized path for empty string is the current directory ('.')
        with self.assertRaises(configparser.NoOptionError):
            conf_cfg.get_external_plugins_dir()

    def test_external_dir_empty(self):
        conf_cfg = self.init(
            dedent(
                r"""
            [b3]
            external_plugins_dir:
        """
            )
        )
        # normalized path for empty string is the current directory ('.')
        self.assertEqual(".", conf_cfg.get_external_plugins_dir())

    def test_external_dir(self):
        conf_cfg = self.init(
            dedent(
                r"""
            [b3]
            external_plugins_dir: f00
        """
            )
        )
        # normalized path for empty string is the current directory ('.')
        self.assertEqual("f00", conf_cfg.get_external_plugins_dir())

    def test_plugins_missing(self):
        conf_cfg = self.init(
            dedent(
                r"""
            [plugins]
        """
            )
        )
        # normalized path for empty string is the current directory ('.')
        self.assertListEqual([], conf_cfg.get_plugins())

    def test_plugins(self):
        conf_cfg = self.init(
            dedent(
                r"""
            [b3]
            disabled_plugins: adv, tk

            [plugins]
            admin: @b3/conf/plugin_admin.ini
            adv: @b3/conf/plugin_adv.ini
            censor: @b3/conf/plugin_censor.ini
            cmdmanager: @b3/conf/plugin_cmdmanager.ini
            tk: @b3/conf/plugin_tk.ini

            [plugins_custom_path]
            cmdmanager: /somewhere/else
        """
            )
        )
        # normalized path for empty string is the current directory ('.')
        expected_result = [
            {
                "name": "admin",
                "conf": "@b3/conf/plugin_admin.ini",
                "disabled": False,
                "path": None,
            },
            {
                "name": "adv",
                "conf": "@b3/conf/plugin_adv.ini",
                "disabled": True,
                "path": None,
            },
            {
                "name": "censor",
                "conf": "@b3/conf/plugin_censor.ini",
                "disabled": False,
                "path": None,
            },
            {
                "name": "cmdmanager",
                "conf": "@b3/conf/plugin_cmdmanager.ini",
                "disabled": False,
                "path": "/somewhere/else",
            },
            {
                "name": "tk",
                "conf": "@b3/conf/plugin_tk.ini",
                "disabled": True,
                "path": None,
            },
        ]
        self.assertListEqual(expected_result, conf_cfg.get_plugins())
