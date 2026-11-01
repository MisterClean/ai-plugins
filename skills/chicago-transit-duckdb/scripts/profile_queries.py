#!/usr/bin/env python3
"""Run native query metrics and optionally compare equivalent raw JSON/Parquet queries."""
import argparse
import csv
import datetime as dt
import json
import math
import os
from pathlib import Path
import platform
import random
import re
import statistics
import sys
import time
from transit_archive import connect,json_select,normalized_select,quote,rows,SCHEMAS,calendar_bounds,file_hash

QUERIES=Path(__file__).parent/'queries'

def parameters(sql,available):
    names=set(re.findall(r'\$([a-z_]+)',sql))
    return {k:available[k] for k in names}

def equivalent(a,b):
    if len(a)!=len(b):return False
    for ra,rb in zip(a,b):
        if set(ra)!=set(rb):return False
        for k,x in ra.items():
            y=rb[k]
            if isinstance(x,float) or isinstance(y,float):
                if x is None or y is None or not math.isclose(x,y,rel_tol=1e-9,abs_tol=1e-7):return False
            elif x!=y:return False
    return True

def write_result(path,result):
    path.with_suffix('.json').write_text(json.dumps(result,indent=2,default=str))
    if result:
        with path.with_suffix('.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(result[0]));w.writeheader();w.writerows(result)

def new_connection(args):
    c=connect(':memory:',threads=args.threads,memory_limit=args.memory_limit)
    c.execute(f'ATTACH {quote(args.db.resolve())} AS transit (READ_ONLY)')
    c.execute('CREATE VIEW native_source AS SELECT * FROM transit.positions')
    return c

def file_sources(c,args,verify=True):
    exists=c.execute("SELECT count(*) FROM duckdb_tables() WHERE database_name='transit' AND table_name='archive_ingest'").fetchone()[0]
    if not exists:raise ValueError('--compare-files needs archive_ingest created by transit_archive.py; omit it for other compatible databases')
    entries=rows(c,'SELECT * FROM transit.archive_ingest WHERE archive_date BETWEEN $start_date::DATE AND $end_date::DATE',dict(start_date=args.start,end_date=args.end))
    if not entries:raise ValueError('No ingested source files in selected window')
    union=[]
    for kind in SCHEMAS:
        paths=[r['local_path'] for r in entries if r['kind']==kind]
        for entry in [r for r in entries if r['kind']==kind]:
            path=Path(entry['local_path'])
            if not path.is_file():raise ValueError('Raw source missing: '+str(path))
            if verify and (path.stat().st_size!=entry['bytes'] or file_hash(path)!=entry['sha256']):
                raise ValueError('Raw source no longer matches ingest manifest: '+str(path))
        if paths:union.append(json_select(kind,paths))
    c.execute('CREATE VIEW json_raw AS '+' UNION ALL '.join(union))
    c.execute('CREATE VIEW json_source AS '+normalized_select('json_raw'))
    return entries

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',type=Path,required=True);p.add_argument('--start',required=True);p.add_argument('--end',required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--compare-files',action='store_true')
    p.add_argument('--repeats',type=int,default=3);p.add_argument('--threads',type=int);p.add_argument('--memory-limit')
    p.add_argument('--kind',choices=list(SCHEMAS),default='bus');p.add_argument('--route',default='66')
    p.add_argument('--window-start',help='ISO timestamp including offset');p.add_argument('--window-end',help='ISO timestamp including offset')
    args=p.parse_args()
    if args.repeats<3:raise ValueError('Use at least three warm repetitions')
    if dt.date.fromisoformat(args.start)>dt.date.fromisoformat(args.end):raise ValueError('start must be <= end')
    if not args.db.is_file():raise ValueError('Database does not exist')
    if args.out.exists() and any(args.out.iterdir()):raise ValueError('Choose an empty output directory to preserve previous results')
    args.out.mkdir(parents=True,exist_ok=True)
    a,_=calendar_bounds(args.start);_,b=calendar_bounds(args.end)
    def iso(ms):return dt.datetime.fromtimestamp(ms/1000,dt.timezone.utc).isoformat()
    available=dict(start_date=args.start,end_date=args.end,kind=args.kind,route=args.route,window_start=args.window_start or iso(a),window_end=args.window_end or iso(b))
    for key in ['window_start','window_end']:
        if dt.datetime.fromisoformat(available[key]).utcoffset() is None:raise ValueError(key+' requires a timezone offset')
    if dt.datetime.fromisoformat(available['window_start'])>=dt.datetime.fromisoformat(available['window_end']):raise ValueError('Window must be nonempty and increasing')
    c=new_connection(args)
    coverage=rows(c,"SELECT kind,min(archive_date) first_day,max(archive_date) last_day,count(DISTINCT archive_date) days_present,count(*) observations FROM native_source WHERE archive_date BETWEEN $start_date::DATE AND $end_date::DATE GROUP BY kind ORDER BY kind",dict(start_date=args.start,end_date=args.end))
    if not coverage:raise ValueError('No observations in selected window')
    expected=(dt.date.fromisoformat(args.end)-dt.date.fromisoformat(args.start)).days+1
    import duckdb
    environment=dict(duckdb=duckdb.__version__,python=platform.python_version(),platform=platform.platform(),machine=platform.machine(),cpu_available=os.cpu_count(),settings=rows(c,"SELECT name,value FROM duckdb_settings() WHERE name IN ('threads','async_threads','memory_limit')"),parameters=available,coverage=coverage,expected_days=expected,repeats=args.repeats,cache='OS cache not flushed; first execution is not a cold-disk measurement',timing_scope='Local query, complete fetch and Python result dictionaries; downloads/build/profiles excluded')
    (args.out/'environment.json').write_text(json.dumps(environment,indent=2,default=str))
    sources=['native'];entries=[]
    if args.compare_files:
        entries=file_sources(c,args)
        write_result(args.out/'source_manifest',[
            {key:entry[key] for key in ['kind','archive_date','source_path','sha256','rows','bytes','source_units']}
            for entry in entries
        ])
        parquet=args.out/'parquet'
        started=time.perf_counter()
        c.execute(f"COPY (SELECT * FROM transit.positions_raw WHERE archive_date BETWEEN DATE {quote(args.start)} AND DATE {quote(args.end)} ORDER BY archive_date,kind,route,ts,vehicle_id) TO {quote(parquet)} (FORMAT PARQUET,PARTITION_BY(kind,archive_date),COMPRESSION ZSTD,ROW_GROUP_SIZE 122880)")
        (args.out/'parquet_build.json').write_text(json.dumps(dict(seconds=time.perf_counter()-started,files=len(list(parquet.rglob('*.parquet'))),bytes=sum(p.stat().st_size for p in parquet.rglob('*.parquet'))),indent=2))
        sources+=['json','parquet']
    c.close()
    templates={p.stem:p.read_text() for p in sorted(QUERIES.glob('*.sql'))}
    tasks=[(source,name) for source in sources for name in templates];random.Random(20261031).shuffle(tasks)
    references={};timings=[]
    for source,name in tasks:
        c=new_connection(args)
        if source=='json':file_sources(c,args,verify=False)
        if source=='parquet':
            c.execute(f"CREATE VIEW parquet_raw AS SELECT * FROM read_parquet({quote(str(args.out/'parquet/**/*.parquet'))},hive_partitioning=true)")
            c.execute('CREATE VIEW parquet_source AS '+normalized_select('parquet_raw'))
        sql=templates[name].format(source=source+'_source');params=parameters(sql,available)
        started=time.perf_counter();result=rows(c,sql,params);first=time.perf_counter()-started
        if name in references and not equivalent(result,references[name]):raise AssertionError('Representation mismatch: '+source+' '+name)
        if name not in references:
            references[name]=result;write_result(args.out/name,result)
        warm=[]
        for _ in range(args.repeats):
            started=time.perf_counter();again=rows(c,sql,params);warm.append(time.perf_counter()-started)
            if not equivalent(again,result):raise AssertionError('Repeat result mismatch')
        profile_path=(args.out/f'profile-{source}-{name}.json').resolve()
        c.execute("SET enable_profiling='json'");c.execute('SET profiling_output='+quote(profile_path))
        rows(c,sql,params);c.execute('PRAGMA disable_profiling')
        profile=json.loads(profile_path.read_text());system=profile.get('system',{});query=profile.get('query',{})
        timings.append(dict(source=source,query=name,result_rows=len(result),first_s=first,warm_median_s=statistics.median(warm),warm_min_s=min(warm),warm_max_s=max(warm),warm_runs_s=warm,peak_engine_buffer_bytes=system.get('peak_buffer_memory'),peak_temp_bytes=system.get('peak_temp_dir_size'),cpu_s=query.get('cpu_time'),rows_scanned=query.get('total_rows_scanned'),row_groups_scanned=query.get('total_row_groups_scanned'),row_groups_total=query.get('total_row_groups_to_scan'),all_results_match=True))
        (args.out/f'query-{source}-{name}.sql').write_text(sql)
        (args.out/f'explain-{source}-{name}.txt').write_text('\n'.join(str(r) for r in c.execute('EXPLAIN ANALYZE '+sql,params).fetchall()))
        c.close();print(source,name,round(statistics.median(warm)*1000,3),'ms',flush=True)
    write_result(args.out/'timings',timings)
    c=new_connection(args)
    summary_sql=(Path(__file__).parent/'summary_hourly.sql').read_text()
    params=parameters(summary_sql,available);started=time.perf_counter();result=rows(c,summary_sql,params);first=time.perf_counter()-started
    if not equivalent(result,references['fleet_hourly']):raise AssertionError('Summary results differ from raw hourly fleet')
    warm=[]
    for _ in range(args.repeats):
        started=time.perf_counter();rows(c,summary_sql,params);warm.append(time.perf_counter()-started)
    (args.out/'summary_timing.json').write_text(json.dumps(dict(first_s=first,warm_median_s=statistics.median(warm),warm_runs_s=warm,all_results_match=True),indent=2))
    (args.out/'summary_query.sql').write_text(summary_sql)
    try:write_result(args.out/'coverage_gaps',rows(c,'SELECT * FROM transit.coverage_gaps WHERE end_ts>$a AND start_ts<$b ORDER BY start_ts',dict(a=a,b=b)))
    except Exception as exc:(args.out/'coverage_unavailable.txt').write_text(str(exc))
    c.close()

if __name__=='__main__':
    try:main()
    except Exception as exc:print(str(exc),file=sys.stderr);raise SystemExit(1)
