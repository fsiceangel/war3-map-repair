import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/war3-map-repair/scripts'))
from jass_compat import audit,repair

class JassSafetyTests(unittest.TestCase):
 def test_unknown_script_is_never_rewritten(self):
  raw=b'function A takes handle h returns integer\nreturn h\nreturn 0\nendfunction\n'
  self.assertEqual(audit(raw)['suspected_return_bug_helpers'],['A'])
  self.assertIsNone(audit(raw)['supported_profile'])
  with self.assertRaises(ValueError):repair(raw)
 def test_patterns_in_comments_and_strings_ignored(self):
  raw=b'// function GetSpellTargetX takes nothing returns real\ncall DisplayTextToPlayer(Player(0),0,0,"function GetSpellTargetY takes nothing returns real")\n'
  self.assertEqual(audit(raw)['potential_native_name_collisions'],[])
 def test_native_name_collision_reported(self):
  raw=b'function GetSpellTargetX takes nothing returns real\nreturn 0.\nendfunction\n'
  self.assertEqual(audit(raw)['potential_native_name_collisions'],['GetSpellTargetX'])
 def test_binary_text_is_auditable(self):
  self.assertIsNone(audit(b'// \xff\x80\n')['supported_profile'])

if __name__=='__main__':unittest.main()
