import contextlib

import b3
import b3.events
import b3.plugin
from b3.config import NoOptionError

__author__ = "ThorN, GrosBedo"
__version__ = "1.5.1"


class StatsPlugin(b3.plugin.Plugin):
    def __init__(self, console, config=None):
        super().__init__(console, config)
        self.mapstatslevel = 0
        self.testscorelevel = 0
        self.topstatslevel = 2
        self.topxplevel = 2
        self.startPoints = 100.0
        self.resetscore = False
        self.resetxp = False
        self.show_awards = False
        self.show_awards_xp = False

    def onLoadConfig(self):
        commands_options = []
        if self.config.has_section("commands"):
            with contextlib.suppress(Exception):
                commands_options = self.config.options("commands")

        def load_command_level(cmd_name):
            matching_options = [
                x for x in commands_options if x.startswith("%s-" % cmd_name)
            ]
            option_name = matching_options[0] if matching_options else cmd_name
            return self.config.getint("commands", option_name)

        try:
            self.mapstatslevel = load_command_level("mapstats")
        except NoOptionError:
            pass
        except Exception as e:
            self.error(e)

        self.info("commands::mapstats level: %s", self.mapstatslevel)
        try:
            self.testscorelevel = load_command_level("testscore")
        except NoOptionError:
            pass
        except Exception as e:
            self.error(e)

        self.info("commands::testscore level: %s", self.testscorelevel)
        try:
            self.topstatslevel = load_command_level("topstats")
        except NoOptionError:
            pass
        except Exception as e:
            self.error(e)

        self.info("commands::topstats level: %s", self.topstatslevel)
        try:
            self.topxplevel = load_command_level("topxp")
        except NoOptionError:
            pass
        except Exception as e:
            self.error(e)

        self.info("commands::topxp level: %s", self.topxplevel)
        try:
            self.startPoints = self.config.getfloat("settings", "startPoints")
        except NoOptionError:
            self.warning(
                "could not find settings/startPoints in config file, "
                "using default: %s" % self.startPoints
            )
        except ValueError as e:
            self.error("could not load settings/startPoints config value: %s" % e)
            self.info(
                "using default value (%s) for settings/startPoints" % self.startPoints
            )

        try:
            self.resetscore = self.config.getboolean("settings", "resetscore")
        except NoOptionError:
            self.warning(
                "could not find settings/resetscore in config file, "
                "using default: %s" % self.resetscore
            )
        except ValueError as e:
            self.error("could not load settings/resetscore config value: %s" % e)
            self.info(
                "using default value (%s) for settings/resetscore" % self.resetscore
            )

        try:
            self.resetxp = self.config.getboolean("settings", "resetxp")
        except NoOptionError:
            self.warning(
                "could not find settings/resetxp in config file, "
                "using default: %s" % self.resetxp
            )
        except ValueError as e:
            self.error("could not load settings/resetxp config value: %s" % e)
            self.info("using default value (%s) for settings/resetxp" % self.resetxp)

        try:
            self.show_awards = self.config.getboolean("settings", "show_awards")
        except NoOptionError:
            self.warning(
                "could not find settings/show_awards in config file, "
                "using default: %s" % self.show_awards
            )
        except ValueError as e:
            self.error("could not load settings/show_awards config value: %s" % e)
            self.info(
                "using default value (%s) for settings/show_awards" % self.show_awards
            )

        try:
            self.show_awards_xp = self.config.getboolean("settings", "show_awards_xp")
        except NoOptionError:
            self.warning(
                "could not find settings/show_awards_xp in config file, "
                "using default: %s" % self.show_awards_xp
            )
        except ValueError as e:
            self.error("could not load settings/show_awards_xp config value: %s" % e)
            self.info(
                "using default value (%s) for settings/show_awards_xp"
                % self.show_awards_xp
            )

    def onStartup(self):
        self.register_commands_from_config()

        self.registerEvent("EVT_CLIENT_DAMAGE_TEAM", self.onDamageTeam)
        self.registerEvent("EVT_CLIENT_KILL_TEAM", self.onTeamKill)
        self.registerEvent("EVT_CLIENT_KILL", self.onKill)
        self.registerEvent("EVT_CLIENT_DAMAGE", self.onDamage)
        self.registerEvent("EVT_GAME_EXIT", self.onShowAwards)
        self.registerEvent("EVT_GAME_MAP_CHANGE", self.onShowAwards)
        self.registerEvent("EVT_GAME_ROUND_START", self.onRoundStart)
        self.registerEvent("EVT_ASSIST", self.onAssist)

    def onShowAwards(self, event):
        if self.show_awards:
            self.cmd_topstats(None)
        if self.show_awards_xp:
            self.cmd_topxp(None)

    def onRoundStart(self, event):
        for _cid, c in self.console.clients.items():
            if c.maxLevel >= self.mapstatslevel:
                try:
                    c.setvar(self, "shotsTeamHit", 0)
                    c.setvar(self, "damageTeamHit", 0)
                    c.setvar(self, "shotsHit", 0)
                    c.setvar(self, "damageHit", 0)
                    c.setvar(self, "shotsGot", 0)
                    c.setvar(self, "damageGot", 0)
                    c.setvar(self, "teamKills", 0)
                    c.setvar(self, "kills", 0)
                    c.setvar(self, "deaths", 0)
                    c.setvar(self, "assists", 0)
                    if self.resetscore:
                        # skill points are reset at the beginning of each map
                        c.setvar(self, "pointsLost", 0)
                        c.setvar(self, "pointsWon", 0)
                        c.setvar(self, "points", self.startPoints)
                    if self.resetxp:
                        c.setvar(self, "experience", 0.0)
                    else:
                        c.var(self, "oldexperience", 0.0).value += c.var(
                            self, "experience", 0.0
                        ).value
                        c.setvar(self, "experience", 0.0)
                except Exception as e:
                    self.error(e)

    def onDamage(self, event):
        killer = event.client
        victim = event.target
        points = int(event.data[0])

        if points > 100:
            points = 100

        killer.var(self, "shotsHit", 0).value += 1
        killer.var(self, "damageHit", 0).value += points
        victim.var(self, "shotsGot", 0).value += 1
        victim.var(self, "damageGot", 0).value += points

    def onDamageTeam(self, event):
        killer = event.client
        points = int(event.data[0])

        if points > 100:
            points = 100

        killer.var(self, "shotsTeamHit", 0).value += 1
        killer.var(self, "damageTeamHit", 0).value += points

    def onKill(self, event):
        killer = event.client
        victim = event.target
        points = int(event.data[0])

        if points > 100:
            points = 100

        killer.var(self, "shotsHit", 0).value += 1
        killer.var(self, "damageHit", 0).value += points

        victim.var(self, "shotsGot", 0).value += 1
        victim.var(self, "damageGot", 0).value += points

        killer.var(self, "kills", 0).value += 1
        victim.var(self, "deaths", 0).value += 1

        val = self.score(killer, victim)
        killer.var(self, "points", self.startPoints).value += val
        killer.var(self, "pointsWon", 0).value += val

        victim.var(self, "points", self.startPoints).value -= val
        victim.var(self, "pointsLost", 0).value += val

        self.updateXP(killer)
        self.updateXP(victim)

    def onTeamKill(self, event):
        killer = event.client
        victim = event.target
        points = int(event.data[0])

        if points > 100:
            points = 100

        killer.var(self, "shotsTeamHit", 0).value += 1
        killer.var(self, "damageTeamHit", 0).value += points

        killer.var(self, "teamKills", 0).value += 1

        val = self.score(killer, victim)
        killer.var(self, "points", self.startPoints).value -= val
        killer.var(self, "pointsLost", 0).value += val

        self.updateXP(killer)
        self.updateXP(victim)

    def onAssist(self, event):
        event.client.var(self, "assists", 0).value += 1

    def updateXP(self, sclient):
        realpoints = (
            sclient.var(self, "pointsWon", 0).value
            - sclient.var(self, "pointsLost", 0).value
        )
        if sclient.var(self, "deaths", 0).value != 0:
            experience = (
                sclient.var(self, "kills", 0).value * realpoints
            ) / sclient.var(self, "deaths", 0).value
        else:
            experience = sclient.var(self, "kills", 0).value * realpoints
        sclient.var(self, "experience", 0.0).value = experience * 1.0

    def score(self, killer, victim):
        k = int(killer.var(self, "points", self.startPoints).value)
        v = int(victim.var(self, "points", self.startPoints).value)

        if k < 1:
            k = 1.00
        if v < 1:
            v = 1.00

        vshift = (float(v) / float(k)) / 2
        points = (15.00 * vshift) + 5

        if points < 1:
            points = 1.00
        elif points > 100:
            points = 100.00

        return round(points, 2)

    def cmd_mapstats(self, data, client, cmd=None):
        """
        [<name>] - list a players stats for the map
        """
        if data:
            if not (sclient := self.findClientPrompt(data, client)):
                return
        else:
            sclient = client

        message = (
            "^3Stats ^7[ %s ^7] K ^2%s ^7D ^3%s ^7A ^5%s ^7TK ^1%s ^7Dmg ^5%s ^7Skill ^3%1.02f ^7XP ^6%s"
            % (
                sclient.exactName,
                sclient.var(self, "kills", 0).value,
                sclient.var(self, "deaths", 0).value,
                sclient.var(self, "assists", 0).value,
                sclient.var(self, "teamKills", 0).value,
                sclient.var(self, "damageHit", 0).value,
                round(sclient.var(self, "points", self.startPoints).value, 2),
                round(
                    sclient.var(self, "oldexperience", 0.0).value
                    + sclient.var(self, "experience", 0.0).value,
                    2,
                ),
            )
        )

        cmd.sayLoudOrPM(client, message)

    def cmd_testscore(self, data, client, cmd=None):
        """
        <client> - how much skill points you will get if you kill the player
        """
        if not data:
            client.message("^7You must supply a player name to test")
            return

        if not (sclient := self.findClientPrompt(data, client)):
            return
        elif sclient == client:
            client.message("^7You don't get points for killing yourself")
        elif (
            sclient.team in (b3.TEAM_BLUE, b3.TEAM_RED) and sclient.team == client.team
        ):
            client.message("^7You don't get points for killing a team mate")
        else:
            cmd.sayLoudOrPM(
                client,
                f"^3Stats: ^7{client.exactName}^7 will get "
                f"^3{self.score(client, sclient)} ^7skill points "
                f"for killing {sclient.exactName}^7",
            )

    def cmd_topstats(self, data, client=None, cmd=None):
        """
        - list the top 5 map-stats players
        """
        if results := self._top_scores("points", top_n=5):
            if client:
                client.message(f"^3Top Stats:^7 {', '.join(results)}")
            else:
                self.console.say(f"^3Top Stats:^7 {', '.join(results)}")
        else:
            client.message("^3Stats: ^7No top players")

    def cmd_topxp(self, data, client=None, cmd=None):
        """
        - list the top 5 map-stats most experienced players
        """
        if results := self._top_scores("experience", top_n=5):
            if client:
                client.message(f"^3Top Experienced Players:^7 {', '.join(results)}")
            else:
                self.console.say(f"^3Top Experienced Players:^7 {', '.join(results)}")
        else:
            client.message("^3Stats: ^7No top experienced players")

    def _top_scores(self, score_kind, top_n=5):
        scores = [
            (round(c.var(self, score_kind, self.startPoints).value, 2), c.exactName)
            for c in self.console.clients.getList()
            if c.isvar(self, score_kind)
        ]
        scores.sort(reverse=True)
        return [
            f"^3#{i}^7 {name} ^7[^3{score}^7]"
            for i, (score, name) in enumerate(scores[:top_n], start=1)
        ]
