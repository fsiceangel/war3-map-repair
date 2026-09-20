import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/war3-map-repair/scripts'))
from slk import cells,serialize,migrate_models,extend_levels,headers

class TransformTests(unittest.TestCase):
 def test_model_migration_preserves_other_fields(self):
  c={(1,1):'"unitUIID"',(2,1):'"file"',(3,1):'"scale"',(1,2):'"hfoo"',(2,2):'"Units\\Human\\Footman\\Footman"',(3,2):'1.2'}
  new,skin,n=migrate_models(serialize(c),None)
  self.assertEqual(n,1);self.assertIn(b'file=Units\\Human\\Footman\\Footman.mdl',skin)
  self.assertEqual(cells(new),{(1,1):'"unitUIID"',(2,1):'"scale"',(1,2):'"hfoo"',(2,2):'1.2'})
 def test_existing_skin_rejected(self):
  c={(1,1):'"id"',(2,1):'"file"',(1,2):'"hfoo"',(2,2):'"a.mdl"'}
  with self.assertRaises(ValueError):migrate_models(serialize(c),b'[hfoo]\r\nfile=b.mdl')
 def test_preserve_existing_level_five_and_idempotence(self):
  c={(1,1):'"alias"',(2,1):'"DataA4"',(3,1):'"DataA5"',(1,2):'"A000"',(2,2):'4',(3,2):'99'}
  new,n=extend_levels(serialize(c));d=cells(new);h=headers(d)
  self.assertEqual(n,1);self.assertEqual(d[h['DataA5'],2],'99');self.assertEqual(d[h['DataA6'],2],'4')
  self.assertTrue(all(d[k]==v for k,v in c.items()))
  again,n=extend_levels(new);self.assertEqual(n,0);self.assertEqual(cells(again),d)
 def test_quoted_semicolon(self):
  d=b'ID;PWXL;N;E\r\nC;X1;Y1;K"id"\r\nC;X1;Y2;K"a;b"\r\nE\r\n'
  self.assertEqual(cells(serialize(cells(d))),cells(d))

if __name__=='__main__':unittest.main()
