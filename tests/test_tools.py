"""Behavioral checks for malformed timelines, portable search and provenance."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sp = importlib.util.spec_from_file_location('check_storyboard', ROOT / 'scripts/check_storyboard.py')
checker = importlib.util.module_from_spec(sp)
sp.loader.exec_module(checker)

class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'assets/storyboard-example.json').read_text(encoding='utf-8'))

    def test_original_example(self):
        errors, warnings = checker.validate(self.data)
        self.assertEqual(errors, [])
        self.assertTrue(any('试读' in x for x in warnings))

    def test_gap(self):
        self.data['shots'][1]['start'] = 6
        self.assertTrue(any('空隙' in x for x in checker.validate(self.data)[0]))

    def test_overlap(self):
        self.data['shots'][1]['start'] = 4
        self.assertTrue(any('重叠' in x for x in checker.validate(self.data)[0]))

    def test_wrong_total(self):
        self.data['duration_seconds'] = 16
        self.assertTrue(any('不一致' in x for x in checker.validate(self.data)[0]))

    def test_undefined_subject(self):
        self.data['shots'][1]['subjects'] = ['missing_product']
        self.assertTrue(any('未定义主体' in x for x in checker.validate(self.data)[0]))

    def test_duplicate_id(self):
        self.data['shots'][1]['id'] = '01'
        self.assertTrue(any('id 重复' in x for x in checker.validate(self.data)[0]))

    def test_invalid_numeric_values(self):
        for value in [True, float('inf'), float('nan'), '15', None, -1, 0]:
            with self.subTest(value=value):
                self.data['duration_seconds'] = value
                self.assertTrue(checker.validate(self.data)[0])

    def test_nan_start(self):
        self.data['shots'][0]['start'] = float('nan')
        self.assertTrue(checker.validate(self.data)[0])

    def test_inverted_and_zero_intervals(self):
        for end in [0, -1]:
            self.data['shots'][0]['end'] = end
            self.assertTrue(checker.validate(self.data)[0])

    def test_malformed_objects_do_not_crash(self):
        for value in [None, [], 'text', {'shots':[]}, {'shots':[None]}, {'shots':[{'id': []}]}]:
            with self.subTest(value=value):
                self.assertTrue(checker.validate(value)[0])

    def test_optional_no_character_landscape(self):
        d={'duration_seconds':4,'aspect_ratio':'16:9','shots':[{'id':'a','start':0,'end':4,'scene':'雨后湖面','action':'水波扩散','camera':'固定全景'}]}
        self.assertEqual(checker.validate(d)[0], [])

    def test_small_float_roundoff(self):
        self.data['shots'][1]['start'] += 1e-8
        self.assertEqual(checker.validate(self.data)[0], [])

    def test_missing_camera(self):
        del self.data['shots'][0]['camera']
        self.assertTrue(checker.validate(self.data)[0])

    def test_aspect_ratio(self):
        for ratio in ['0:16', '9:0', 'vertical', None]:
            self.data['aspect_ratio']=ratio
            self.assertTrue(checker.validate(self.data)[0])

    def test_cli_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'bad.json';path.write_text('{bad')
            proc=subprocess.run([sys.executable,str(ROOT/'scripts/check_storyboard.py'),str(path)],capture_output=True,text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertIn('读取失败',proc.stderr)

class SearchTests(unittest.TestCase):
    def run_search(self,*args):
        with tempfile.TemporaryDirectory() as tmp:
            return subprocess.run([sys.executable,str(ROOT/'scripts/search_library.py'),*args],cwd=tmp,capture_output=True,text=True)

    def test_portable_keyword_query(self):
        proc=self.run_search('环绕','--kind','prompts','--limit','3')
        self.assertEqual(proc.returncode,0)
        result=json.loads(proc.stdout)
        self.assertEqual(result['returned'],3)
        self.assertTrue(all('locator' in x and 'caution' in x for x in result['results']))

    def test_duplicate_source_resolves(self):
        result=json.loads(self.run_search('--source','S096','--kind','sources').stdout)
        self.assertEqual(result['canonical_source'],'S095')
        self.assertEqual({r['id'] for r in result['results']},{'S095','S096'})

    def test_source_filter(self):
        result=json.loads(self.run_search('--source','s145','--kind','prompts','--limit','50').stdout)
        self.assertEqual(result['total_matches'],50)
        self.assertTrue(all(r['source_id']=='S145' for r in result['results']))

    def test_multiple_terms_and_empty_result(self):
        result=json.loads(self.run_search('环绕 不存在的检索词987654321').stdout)
        self.assertEqual(result['total_matches'],0)

    def test_invalid_source_and_limit(self):
        for args in [('--source','S999'),('--limit','0'),('--limit','100')]:
            self.assertEqual(self.run_search(*args).returncode,2)

if __name__ == '__main__':
    unittest.main()
