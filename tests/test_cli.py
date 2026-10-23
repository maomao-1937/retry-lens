import json, pathlib, subprocess, sys, tempfile, unittest
SCRIPT=pathlib.Path(__file__).resolve().parents[1].joinpath('retry_lens.py')
class RetryTests(unittest.TestCase):
 def run_rows(self, rows, *args):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'events.jsonl'; p.write_text('\n'.join(json.dumps(x) for x in rows),encoding='utf-8')
   return subprocess.run([sys.executable,str(SCRIPT),str(p),'--format','json',*args],capture_output=True,text=True)
 def event(self,a=1,s='failure',d=1): return dict(operation_id='a',attempt=a,status=s,duration_ms=d)
 def test_empty_log_is_not_clean(self):
  r=self.run_rows([]); self.assertEqual(r.returncode,2); self.assertIn('no events',r.stderr)
 def test_unordered(self):
  r=self.run_rows([self.event(2,'success'),self.event()]); self.assertEqual(r.returncode,0,r.stderr); self.assertEqual(json.loads(r.stdout)['operations'][0]['duration_ms'],2)
 def test_after_success(self):
  r=self.run_rows([self.event(1,'success'),self.event(2)]); self.assertEqual(r.returncode,1); self.assertIn('attempted_after_success',r.stdout)
 def test_repeated_success(self):
  r=self.run_rows([self.event(2,'success'),self.event(1,'success')]); self.assertEqual(r.returncode,1); self.assertIn('repeated_success',r.stdout)
 def test_duplicate_attempt(self): self.assertEqual(self.run_rows([self.event(),self.event()]).returncode,2)
 def test_gaps_review(self):
  r=self.run_rows([self.event(3)]); self.assertEqual(r.returncode,1); self.assertEqual(json.loads(r.stdout)['status'],'review')
 def test_threshold(self):
  r=self.run_rows([self.event(),self.event(2)],'--max-attempts','1'); self.assertEqual(r.returncode,1); self.assertIn('max_attempts_exceeded',r.stdout)
 def test_invalid_threshold(self): self.assertEqual(self.run_rows([],'--max-attempts','0').returncode,2)
 def test_nonfinite(self): self.assertEqual(self.run_rows([self.event(d=float('nan'))]).returncode,2)
 def test_bool_attempt(self): self.assertEqual(self.run_rows([self.event(True)]).returncode,2)
 def test_negative_duration(self): self.assertEqual(self.run_rows([self.event(d=-1)]).returncode,2)
 def test_unicode_line_separator_inside_string(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'x'; e=self.event(); e['operation_id']='a b'; p.write_text(json.dumps(e,ensure_ascii=False),encoding='utf-8'); r=subprocess.run([sys.executable,str(SCRIPT),str(p)],capture_output=True,text=True); self.assertEqual(r.returncode,0,r.stderr)
 def test_json_duplicate_keys(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'x'; p.write_text('{"operation_id":"a","attempt":1,"attempt":2,"status":"failure","duration_ms":1}'); r=subprocess.run([sys.executable,str(SCRIPT),str(p)],capture_output=True,text=True); self.assertEqual(r.returncode,2); self.assertIn('error: invalid event',r.stderr)
 def test_help(self): self.assertEqual(subprocess.run([sys.executable,str(SCRIPT),'--help'],capture_output=True).returncode,0)
if __name__=='__main__': unittest.main()
