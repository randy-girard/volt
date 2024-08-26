import unittest

from volt.utils.regex_engine import RegexEngine
from volt.models.profile import Profile

class RegexEngineTest(unittest.TestCase):
    def test_another_ch_example(self):
        engine = RegexEngine(None)
        engine.compile("^({s}|You) shouts?, 'GG +([\dA-Za-z]+) +CH +-- +({s}) *'$")
        matches = engine.match("Caster shouts, 'GG 001 CH -- Player'")
        result = engine.execute("${2} : ${3} : ${1}", matches=matches)
        self.assertEqual(result, "Player : 001 : Caster")
            
    def test_ch(self):
        engine = RegexEngine(None)
        engine.compile("^({s}|You) shouts?, 'GG ([\dA-Za-z]{1,4} CH -- {s}) *'$")
        matches = engine.match("Caster shouts, 'GG 001 CH -- Player'")
        result = engine.execute("${1} > ${2}", matches=matches)
        self.assertEqual(result, "Caster > Player")

    def test_tash(self):
        engine = RegexEngine(None)
        engine.compile("^(?:(?:[^ ]+) tells the guil)d, 'TASH(?>ED)?\s+-+\s+{s}\s*'$")
        matches = engine.match("Caster tells the guild, 'TASHED -- Player'")
        result = engine.execute("TASH - {s}", matches=matches)
        self.assertEqual(result, "TASH - Player")

    def test_character_name_replace(self):
        profile = Profile(name="Caster")

        engine = RegexEngine(profile)
        engine.compile("^{c} says, 'CB -- ^{t}'")
        matches = engine.match("Caster says, 'CB -- Player'")
        result = engine.execute("Chloroblast ( ^{t} )", matches=matches)
        self.assertEqual(result, "Chloroblast ( Player )")

    def test_slain_message_other(self):
        engine = RegexEngine(None)
        engine.compile("({s} has been slain by|you have slain {s1}!)")
        matches = engine.match("King Gragnar has been slain by Bob")
        result = engine.execute("Spawn - {s}{s1}", matches=matches)
        self.assertEqual(result, "Spawn - King Gragnar")

    def test_slain_message_you(self):
        engine = RegexEngine(None)
        engine.compile("({s} has been slain by|you have slain {s1}!)")
        matches = engine.match("You have slain King Gragnar!")
        result = engine.execute("Spawn - {s}{s1}", matches=matches)
        self.assertEqual(result, "Spawn - King Gragnar")

    def test_coth_message(self):
        engine = RegexEngine(None)
        engine.compile("^(?:(?<cother>[^ ]+) tells the group), 'COTH (?<cothee>[^']+)'")
        matches = engine.match("Caster tells the group, 'COTH Player'")
        result = engine.execute("COTH ${cothee} (${cother})", matches=matches)
        self.assertEqual(result, "COTH Player (Caster)")

    def test_coth_guild_message(self):
        engine = RegexEngine(None)
        engine.compile("^(?:(?<cother>[^ ]+) tells the guild), 'COTH (?<cothee>[^']+)")
        matches = engine.match("Caster tells the guild, 'COTH -- Player'")
        result = engine.execute("COTH ${cothee}", matches=matches)
        self.assertEqual(result, "COTH -- Player")

    def test_ch_chain_message(self):
        engine = RegexEngine(None)
        engine.compile("^(?<caster>[^ ]+) (?:(?:tell(?>s the g(?>uild|roup)| your party)|say(?:s?(?> out of character)?| to your guild)|shouts?|auctions?)), '(?<num>(\w+)) CH - (?<target>.*?)'$")
        matches = engine.match("Caster tells the guild, '001 CH - Player'")
        result = engine.execute("${num} CH -- ${target} (${caster})", matches=matches)
        self.assertEqual(result, "001 CH -- Player (Caster)")

    def test_harmony_message(self):
        engine = RegexEngine(None)
        engine.compile("tells the guild, 'HARMONY -- ^{t}'")
        matches = engine.match("Caster tells the guild, 'HARMONY -- Mob'")
        result = engine.execute("Harmony ( {t} )", matches=matches)
        self.assertEqual(result, "Harmony ( Mob )")

    def test_regex_groups(self):
        engine = RegexEngine(None)
        engine.compile("^You (backstab) .* for (\d+) points of damage\.$")
        matches = engine.match("You backstab Mob for 100 points of damage.")
        result = engine.execute("${2}", matches=matches)
        self.assertEqual(result, "100")

    def test_poison_message(self):
        engine = RegexEngine(None)
        engine.compile("^{s}(?: has be)en poisoned\.$")
        matches = engine.match("Player has been poisoned.")
        result = engine.execute("{s} - Envenomed Bolt", matches=matches)
        self.assertEqual(result, "Player - Envenomed Bolt")

    def test_s_to_one(self):
        engine = RegexEngine(None)
        engine.compile(".*COTH -- {s}.*")
        matches = engine.match("Cother tells the guild, 'COTH -- Player'")
        result = engine.execute("COTH -- ${1}", matches=matches)
        self.assertEqual(result, "COTH -- Player'")

    def test_rez(self):
        engine = RegexEngine(None)
        engine.compile("^{s1} tells the guild, 'R(ez|EZ) -- {s2}'$")
        matches = engine.match("Player tells the guild, 'REZ -- Dead'")
        result = engine.execute("{s1} REZZING {s2}", matches=matches)
        self.assertEqual(result, "Player REZZING Dead")

    def test_timestamp_matching(self):
        engine = RegexEngine(None)
        engine.compile("x{TS}-{S};")
        matches = engine.match("x10:00-something; is not online at this time.")
        result = engine.execute("{S}", matches=matches)
        self.assertEqual(engine.duration, 600)
        self.assertEqual(result, "something")
