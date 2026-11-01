#!/usr/bin/env python3
"""Offline smoke tests; tiny synthetic inputs, no remote or production writes."""
import datetime as dt
import gzip
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from transit_archive import calendar_bounds,connect,file_hash,initialize,ingest_file,select_files,export_parquet,quote,normalized_select,rows

class TransitTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.c=connect(self.root/'test.duckdb',threads=2,memory_limit='512MB');initialize(self.c)
        self.day='2026-10-30';self.ts=calendar_bounds(self.day)[0]+8*3600000
    def tearDown(self):self.c.close();self.tmp.cleanup()
    def fixture(self,kind,observations):
        p=self.root/f'{kind}-{self.day}.ndjson.gz'
        with gzip.open(p,'wt') as f:
            for row in observations:f.write(json.dumps(row)+'\n')
        return dict(kind=kind,date=self.day,path=f'positions/{kind}/2026/10/{self.day}.ndjson.gz',rows=len(observations),bytes=p.stat().st_size,sha256=file_hash(p)),p
    def base(self,kind):
        row=dict(ts=self.ts,route='red' if kind=='train' else '66' if kind=='bus' else 'BNSF',vehicle_id='001',lat=41.9,lon=-87.6)
        if kind=='bus':row.update(vehicle_ts=self.ts-15000,pid='123',pdist=1000)
        if kind=='train':row.update(approx=0,direction='1')
        if kind=='metra':row.update(vehicle_ts=(self.ts-30000)//1000,trip_id='trip')
        return row
    def test_dst_calendar_and_selection(self):
        self.assertEqual((calendar_bounds('2026-03-08')[1]-calendar_bounds('2026-03-08')[0])//60000,1380)
        self.assertEqual((calendar_bounds('2026-11-01')[1]-calendar_bounds('2026-11-01')[0])//60000,1500)
        m,p=self.fixture('bus',[self.base('bus')]);index={'days':[{'date':self.day,'files':{'bus':m}}]}
        self.assertEqual(select_files(index,days=1,kinds=['bus'],as_of='2026-10-31')[0]['date'],self.day)
        with self.assertRaisesRegex(ValueError,'not complete'):select_files(index,end=self.day,days=1,kinds=['bus'],as_of=self.day)
        with self.assertRaisesRegex(ValueError,'not published'):select_files(index,days=2,kinds=['bus'],as_of='2026-10-31')
    def test_normalization_dedup_idempotency(self):
        for kind in ['bus','train','metra']:
            r=self.base(kind);observations=[r,r.copy()] if kind=='train' else [r]
            if kind=='train':observations.append(dict(r,ts=self.ts+30000,approx=1))
            m,p=self.fixture(kind,observations);ingest_file(self.c,m,p)
            self.assertEqual(ingest_file(self.c,m,p)['status'],'skipped')
        self.assertEqual(self.c.execute("SELECT ts-vehicle_ts FROM positions WHERE kind='metra'").fetchone()[0],30000)
        self.assertEqual(self.c.execute('SELECT count(*) FROM train_exact_positions').fetchone()[0],1)
        self.assertEqual(self.c.execute("SELECT vehicles FROM fleet_minutes WHERE kind='train'").fetchone()[0],1)
        self.assertEqual(self.c.execute('SELECT count(*) FROM positions_raw').fetchone()[0],5)
    def test_reject_changed_hash_and_mixed_units(self):
        r=self.base('metra');m,p=self.fixture('metra',[r]);ingest_file(self.c,m,p)
        m2,p2=self.fixture('metra',[dict(r,vehicle_id='002')])
        with self.assertRaisesRegex(ValueError,'source changed'):ingest_file(self.c,m2,p2)
        self.assertEqual(self.c.execute('SELECT count(*) FROM positions_raw').fetchone()[0],1)
        c=connect(self.root/'mixed.duckdb');initialize(c)
        m3,p3=self.fixture('metra',[r,dict(r,vehicle_ts=r['vehicle_ts']*1000)])
        with self.assertRaisesRegex(ValueError,'mixed'):ingest_file(c,m3,p3)
        self.assertEqual(c.execute('SELECT count(*) FROM positions_raw').fetchone()[0],0);c.close()
    def test_reject_invalid_approximation_and_empty_ids(self):
        r=self.base('train');m,p=self.fixture('train',[dict(r,approx=2)])
        with self.assertRaisesRegex(Exception,'approx must'):ingest_file(self.c,m,p)
        m,p=self.fixture('bus',[dict(self.base('bus'),vehicle_id='')])
        with self.assertRaisesRegex(ValueError,'validation failed'):ingest_file(self.c,m,p)
        self.assertEqual(self.c.execute('SELECT count(*) FROM positions_raw').fetchone()[0],0)
    def test_committed_modes_survive_new_process(self):
        for kind in ['bus','train','metra']:
            m,p=self.fixture(kind,[self.base(kind)]);ingest_file(self.c,m,p)
        self.c.close()
        try:
            result=subprocess.run([sys.executable,'-c',"import duckdb,sys; c=duckdb.connect(sys.argv[1],read_only=True); print(c.execute('SELECT count(*) FROM positions').fetchone()[0]); c.close()",str(self.root/'test.duckdb')],check=True,capture_output=True,text=True)
            self.assertEqual(result.stdout.strip(),'3')
        finally:self.c=connect(self.root/'test.duckdb',threads=2,memory_limit='512MB')
    def test_all_queries_parquet_and_coverage(self):
        for kind in ['bus','train','metra']:
            r=self.base(kind);m,p=self.fixture(kind,[r,dict(r,ts=self.ts+60000)]);ingest_file(self.c,m,p)
        params=dict(start_date=self.day,end_date=self.day,kind='bus',route='66',window_start='2026-10-30T08:00:00-05:00',window_end='2026-10-30T09:00:00-05:00')
        from profile_queries import parameters,equivalent
        for p in (Path(__file__).parent/'queries').glob('*.sql'):
            sql=p.read_text().format(source='positions');self.assertIsInstance(rows(self.c,sql,parameters(sql,params)),list)
        count=self.c.execute('SELECT sum(missing_minutes) FROM coverage_gaps').fetchone()[0]
        self.assertEqual(count,1440-2)
        out=self.root/'parquet';export_parquet(self.c,out)
        self.c.execute('CREATE VIEW p_raw AS SELECT * FROM read_parquet('+quote(out/'**/*.parquet')+',hive_partitioning=true)')
        self.c.execute('CREATE VIEW p AS '+normalized_select('p_raw'))
        sql=(Path(__file__).parent/'queries/freshness.sql').read_text()
        self.assertTrue(equivalent(rows(self.c,sql.format(source='positions'),parameters(sql,params)),rows(self.c,sql.format(source='p'),parameters(sql,params))))
        with self.assertRaisesRegex(ValueError,'empty'):export_parquet(self.c,out)

    def test_profiler_file_comparison(self):
        dated_parent=self.root/'2020-01-01';dated_parent.mkdir()
        for kind in ['bus','train','metra']:
            r=self.base(kind);m,p=self.fixture(kind,[r,dict(r,ts=self.ts+60000)])
            moved=p.rename(dated_parent/p.name)
            ingest_file(self.c,m,moved)
        # Fetching TIMESTAMPTZ metadata also checks the declared pytz dependency.
        self.assertIsNotNone(self.c.execute('SELECT poll_ts FROM positions LIMIT 1').fetchone()[0].tzinfo)
        self.c.close()
        try:
            out=self.root/'profiles'
            result=subprocess.run([
                sys.executable,str(Path(__file__).with_name('profile_queries.py')),
                '--db',str(self.root/'test.duckdb'),'--start',self.day,'--end',self.day,
                '--out',str(out),'--compare-files','--threads','2','--memory-limit','512MB',
            ],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            timings=json.loads((out/'timings.json').read_text(encoding='utf-8'))
            self.assertEqual({r['source'] for r in timings},{'native','json','parquet'})
            self.assertEqual(len(timings),3*len(list(Path(__file__).with_name('queries').glob('*.sql'))))
            self.assertTrue(all(r['all_results_match'] for r in timings))
        finally:self.c=connect(self.root/'test.duckdb',threads=2,memory_limit='512MB')

    def test_dst_sql_denominators_and_repeated_hour(self):
        self.day='2026-11-01'
        a,b=calendar_bounds(self.day)
        r=self.base('bus')
        # Both local 01:30 instants, one before and one after the fallback.
        m,p=self.fixture('bus',[dict(r,ts=a+90*60000),dict(r,ts=a+150*60000)])
        ingest_file(self.c,m,p)
        self.assertEqual(self.c.execute('SELECT sum(missing_minutes) FROM coverage_gaps').fetchone()[0],1498)
        params=dict(start_date=self.day,end_date=self.day)
        sql=Path(__file__).with_name('queries').joinpath('coverage_daily.sql').read_text(encoding='utf-8')
        coverage=rows(self.c,sql.format(source='positions'),params)
        self.assertEqual(coverage[0]['expected_calendar_minutes'],1500)
        sql=Path(__file__).with_name('queries').joinpath('fleet_hourly.sql').read_text(encoding='utf-8')
        hourly=rows(self.c,sql.format(source='positions'),params)
        self.assertEqual(len(hourly),2)
        self.assertEqual(hourly[1]['hour_start_ms']-hourly[0]['hour_start_ms'],3600000)
        self.assertTrue(all(r['expected_calendar_minutes']==60 for r in hourly))

    def test_movement_exclusions_preserve_adjacency(self):
        r=self.base('train')
        observations=[dict(r,ts=self.ts+i*30000,lat=41.9+i*0.001) for i in range(5)]
        observations[1]['approx']=1
        observations[3]['direction']='5'
        m,p=self.fixture('train',observations);ingest_file(self.c,m,p)
        sql=Path(__file__).with_name('queries').joinpath('movement_diagnostics.sql').read_text(encoding='utf-8')
        result=rows(self.c,sql.format(source='positions'),dict(start_date=self.day,end_date=self.day,kind='train',route='red'))[0]
        self.assertEqual(result['candidate_pairs'],4)
        self.assertEqual(result['estimated_or_unknown_endpoint_pairs'],2)
        self.assertEqual(result['continuity_change_pairs'],2)
        self.assertEqual(result['usable_pairs'],0)

    def test_movement_rejects_conflicting_poll_endpoints(self):
        r=self.base('bus')
        middle=dict(r,ts=self.ts+30000,vehicle_ts=r['vehicle_ts']+30000)
        observations=[r,middle,dict(middle,lat=42.0),dict(r,ts=self.ts+60000,vehicle_ts=r['vehicle_ts']+60000)]
        m,p=self.fixture('bus',observations);ingest_file(self.c,m,p)
        sql=Path(__file__).with_name('queries').joinpath('movement_diagnostics.sql').read_text(encoding='utf-8')
        result=rows(self.c,sql.format(source='positions'),dict(start_date=self.day,end_date=self.day,kind='bus',route='66'))[0]
        self.assertEqual(result['ambiguous_poll_pairs'],3)
        self.assertEqual(result['usable_pairs'],0)

if __name__=='__main__':unittest.main(verbosity=2)
