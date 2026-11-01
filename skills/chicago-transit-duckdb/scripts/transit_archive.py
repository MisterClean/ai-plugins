#!/usr/bin/env python3
"""Validated incremental position ingestion and Parquet export. Python 3.10+, DuckDB 2.x."""
import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

ORIGIN='https://data.chicagotransitalerts.app/'
INDEX=ORIGIN+'positions/index.json'
CHICAGO=ZoneInfo('America/Chicago')
SCHEMAS={
 'bus':dict(ts='BIGINT',route='VARCHAR',pid='VARCHAR',vehicle_id='VARCHAR',destination='VARCHAR',lat='DOUBLE',lon='DOUBLE',pdist='DOUBLE',heading='DOUBLE',vehicle_ts='BIGINT',sched_start_sec='INTEGER',sched_start_date='VARCHAR'),
 'train':dict(ts='BIGINT',route='VARCHAR',direction='VARCHAR',vehicle_id='VARCHAR',destination='VARCHAR',lat='DOUBLE',lon='DOUBLE',approx='INTEGER',next_station='VARCHAR'),
 'metra':dict(ts='BIGINT',route='VARCHAR',vehicle_id='VARCHAR',lat='DOUBLE',lon='DOUBLE',heading='DOUBLE',vehicle_ts='BIGINT',trip_id='VARCHAR')}
FIELDS=dict(ts='BIGINT',route='VARCHAR',vehicle_id='VARCHAR',lat='DOUBLE',lon='DOUBLE',vehicle_ts='BIGINT',approx='BOOLEAN',direction='VARCHAR',pid='VARCHAR',pdist='DOUBLE',destination='VARCHAR',heading='DOUBLE',sched_start_sec='INTEGER',sched_start_date='VARCHAR',next_station='VARCHAR',trip_id='VARCHAR')
NORMALIZED="CASE WHEN kind='metra' AND vehicle_ts BETWEEN 1000000000 AND 9999999999 THEN vehicle_ts*1000 ELSE vehicle_ts END"

def quote(value):
    return "'"+str(value).replace("'","''")+"'"

def connect(path,read_only=False,threads=None,memory_limit=None):
    import duckdb
    if duckdb.__version__.split('.')[0]!='2':
        raise RuntimeError('DuckDB 2.x required; actual version: '+duckdb.__version__)
    c=duckdb.connect(str(path),read_only=read_only)
    c.execute("SET TimeZone='UTC';SET preserve_insertion_order=false")
    c.execute('SET threads='+str(threads or min(8,os.cpu_count() or 1)))
    if memory_limit:c.execute('SET memory_limit='+quote(memory_limit))
    return c

def rows(c,sql,params=None):
    q=c.execute(sql,params or {});cols=[x[0] for x in q.description]
    return [dict(zip(cols,r)) for r in q.fetchall()]

def file_hash(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def calendar_bounds(date):
    day=dt.date.fromisoformat(str(date))
    a=dt.datetime.combine(day,dt.time(),CHICAGO)
    b=dt.datetime.combine(day+dt.timedelta(days=1),dt.time(),CHICAGO)
    return int(a.timestamp()*1000),int(b.timestamp()*1000)

def select_files(index,end=None,days=7,kinds=('bus','train','metra'),as_of=None):
    if days<1:raise ValueError('days must be positive')
    today=dt.date.fromisoformat(as_of) if as_of else dt.datetime.now(CHICAGO).date()
    last=dt.date.fromisoformat(end) if end else today-dt.timedelta(days=1)
    if last>=today:raise ValueError('Requested end date is not complete in America/Chicago')
    lookup={d['date']:d['files'] for d in index['days']}
    out=[]
    for i in range(days-1,-1,-1):
        day=(last-dt.timedelta(days=i)).isoformat()
        for kind in kinds:
            if kind not in SCHEMAS:raise ValueError('Unknown mode: '+kind)
            if day not in lookup or kind not in lookup[day]:
                raise ValueError(f'Archive not published for {kind} {day}; no older dates substituted')
            m=dict(lookup[day][kind]);expected=f'positions/{kind}/{day[:4]}/{day[5:7]}/{day}.ndjson.gz'
            if m.get('path')!=expected:raise ValueError('Unexpected archive path: '+str(m.get('path')))
            if not re.fullmatch('[0-9a-f]{64}',m.get('sha256','')):raise ValueError('Invalid SHA-256')
            if not isinstance(m.get('rows'),int) or m['rows']<0:raise ValueError('Invalid row count')
            if not isinstance(m.get('bytes'),int) or m['bytes']<0:raise ValueError('Invalid byte size')
            out.append(dict(m,kind=kind,date=day))
    return out

def fetch_index(location,raw_dir):
    if location.startswith('https://'):
        if location!=INDEX:raise ValueError('Use the canonical index URL or a pinned local index')
        path=raw_dir/'index.download.json'
        subprocess.run(['curl','-fLsS','--max-time','60',location,'-o',str(path)],check=True)
    else:path=Path(location)
    obj=json.loads(path.read_text())
    if obj.get('timezone') not in (None,'America/Chicago'):raise ValueError('Unexpected archive timezone')
    return obj

def ensure_file(meta,raw_dir):
    path=raw_dir/f"{meta['kind']}-{meta['date']}.ndjson.gz"
    if path.exists() and path.stat().st_size==meta['bytes'] and file_hash(path)==meta['sha256']:
        return path
    temp=path.with_suffix('.part')
    try:
        subprocess.run(['curl','-fLsS','--retry','2','--max-time','180',ORIGIN+meta['path'],'-o',str(temp)],check=True)
        if temp.stat().st_size!=meta['bytes'] or file_hash(temp)!=meta['sha256']:
            raise ValueError('Size or SHA-256 mismatch: '+str(path))
        temp.replace(path)
    finally:
        if temp.exists():temp.unlink()
    return path

def json_select(kind,paths,date=None):
    cols='{'+','.join(quote(k)+':'+quote(v) for k,v in SCHEMAS[kind].items())+'}'
    files='['+','.join(quote(Path(p).resolve()) for p in paths)+']'
    # Anchor to the archive suffix: workspace parents can also contain ISO dates.
    date_sql='DATE '+quote(date) if date else "regexp_extract(filename,'([0-9]{4}-[0-9]{2}-[0-9]{2})[.]ndjson[.]gz$',1)::DATE"
    fields=[]
    for k,t in FIELDS.items():
        value=k if k in SCHEMAS[kind] else ('false' if k=='approx' else 'NULL::'+t)
        if k=='approx' and kind=='train':
            value="CASE WHEN approx IS NULL OR approx IN (0,1) THEN CAST(approx AS BOOLEAN) ELSE error('approx must be 0, 1, or null') END"
        fields.append(f'CAST({value} AS {t}) AS {k}')
    return f'SELECT {quote(kind)}::VARCHAR kind,{date_sql} archive_date,'+','.join(fields)+f" FROM read_json({files},format='newline_delimited',compression='gzip',columns={cols},filename=true)"

def normalized_select(source):
    return f"SELECT * EXCLUDE(vehicle_ts),vehicle_ts vehicle_ts_raw,{NORMALIZED} vehicle_ts,epoch_ms(ts) AT TIME ZONE 'UTC' poll_ts,epoch_ms({NORMALIZED}) AT TIME ZONE 'UTC' source_ts FROM {source}"

def initialize(c):
    tables={r[0] for r in c.execute('SHOW TABLES').fetchall()}
    if 'positions_raw' in tables and 'archive_ingest' not in tables:
        raise ValueError('Existing positions_raw is not owned by this helper; choose a new database')
    fields=','.join(k+' '+t for k,t in FIELDS.items())
    c.execute('CREATE TABLE IF NOT EXISTS positions_raw(kind VARCHAR,archive_date DATE,'+fields+')')
    c.execute('''CREATE TABLE IF NOT EXISTS archive_ingest(kind VARCHAR,archive_date DATE,sha256 VARCHAR,source_path VARCHAR,local_path VARCHAR,rows BIGINT,bytes BIGINT,source_units VARCHAR,extra_sampled_fields VARCHAR,ingested_at TIMESTAMPTZ DEFAULT current_timestamp,PRIMARY KEY(kind,archive_date))''')
    c.execute('''CREATE TABLE IF NOT EXISTS fleet_minutes(kind VARCHAR,route VARCHAR,archive_date DATE,minute_id BIGINT,vehicles BIGINT)''')
    c.execute('CREATE OR REPLACE VIEW positions AS '+normalized_select('positions_raw'))
    for kind in SCHEMAS:
        c.execute(f"CREATE OR REPLACE VIEW {kind}_positions AS SELECT * FROM positions WHERE kind={quote(kind)}")
    c.execute('CREATE OR REPLACE VIEW train_exact_positions AS SELECT DISTINCT * FROM train_positions WHERE approx=false')
    c.execute('''CREATE OR REPLACE VIEW coverage_gaps AS
WITH expected AS(SELECT r.minute_id FROM archive_ingest i,
range(epoch_ms(i.archive_date::TIMESTAMP AT TIME ZONE 'America/Chicago')//60000,
epoch_ms((i.archive_date+INTERVAL 1 DAY)::TIMESTAMP AT TIME ZONE 'America/Chicago')//60000) r(minute_id) WHERE kind='bus'),
present AS(SELECT DISTINCT minute_id FROM fleet_minutes WHERE kind='bus'),
missing AS(SELECT minute_id FROM expected ANTI JOIN present USING(minute_id)),
g AS(SELECT minute_id,minute_id-row_number() OVER(ORDER BY minute_id) group_id FROM missing)
SELECT min(minute_id)*60000 start_ts,(max(minute_id)+1)*60000 end_ts,count(*) missing_minutes FROM g GROUP BY group_id''')

def ingest_file(c,meta,path):
    path=Path(path).resolve()
    if path.stat().st_size!=meta['bytes'] or file_hash(path)!=meta['sha256']:
        raise ValueError('Input bytes failed manifest verification')
    prior=c.execute('SELECT sha256,rows FROM archive_ingest WHERE kind=? AND archive_date=?',[meta['kind'],meta['date']]).fetchone()
    if prior:
        if prior!=(meta['sha256'],meta['rows']):raise ValueError('Published source changed; rebuild affected data in a new database')
        return dict(kind=meta['kind'],date=meta['date'],status='skipped',rows=meta['rows'])
    extra=set()
    with gzip.open(path,'rt') as f:
        for _,line in zip(range(100),f):extra.update(set(json.loads(line))-set(SCHEMAS[meta['kind']]))
    started=time.perf_counter()
    c.execute('CREATE OR REPLACE TEMP TABLE stage AS '+json_select(meta['kind'],[path],meta['date']))
    a,b=calendar_bounds(meta['date'])
    qa=rows(c,'''SELECT count(*) n,count(*) FILTER(WHERE ts IS NULL OR route IS NULL OR trim(route)='' OR vehicle_id IS NULL OR trim(vehicle_id)='' OR lat IS NULL OR lon IS NULL) missing,
count(*) FILTER(WHERE NOT isfinite(lat) OR NOT isfinite(lon) OR lat NOT BETWEEN -90 AND 90 OR lon NOT BETWEEN -180 AND 180) invalid_coordinates,
count(*) FILTER(WHERE ts<$a OR ts>=$b) wrong_date FROM stage''',dict(a=a,b=b))[0]
    if qa['n']!=meta['rows'] or qa['missing'] or qa['invalid_coordinates'] or qa['wrong_date']:
        raise ValueError('Data validation failed: '+json.dumps(qa))
    units=[r[0] for r in c.execute("""SELECT DISTINCT CASE WHEN vehicle_ts IS NULL THEN NULL
WHEN kind='metra' AND vehicle_ts BETWEEN 1000000000 AND 9999999999 THEN 'seconds'
WHEN vehicle_ts BETWEEN 1000000000000 AND 9999999999999 THEN 'milliseconds' ELSE 'unknown' END u FROM stage WHERE vehicle_ts IS NOT NULL""").fetchall()]
    if 'unknown' in units or len(units)>1:raise ValueError('Unrecognized or mixed source timestamp units: '+str(units))
    c.execute('BEGIN')
    try:
        c.execute('INSERT INTO positions_raw SELECT * FROM stage ORDER BY kind,route,ts,vehicle_id')
        c.execute('INSERT INTO fleet_minutes SELECT kind,route,archive_date,ts//60000 minute_id,count(DISTINCT vehicle_id) vehicles FROM stage GROUP BY kind,route,archive_date,minute_id ORDER BY kind,route,minute_id')
        c.execute('INSERT INTO archive_ingest(kind,archive_date,sha256,source_path,local_path,rows,bytes,source_units,extra_sampled_fields) VALUES (?,?,?,?,?,?,?,?,?)',
                  [meta['kind'],meta['date'],meta['sha256'],meta['path'],str(path),meta['rows'],meta['bytes'],units[0] if units else None,json.dumps(sorted(extra))])
        c.execute('COMMIT')
    except Exception:
        c.execute('ROLLBACK');raise
    finally:c.execute('DROP TABLE IF EXISTS stage')
    c.execute('CHECKPOINT')
    return dict(kind=meta['kind'],date=meta['date'],status='ingested',rows=meta['rows'],seconds=time.perf_counter()-started,source_units=units,extra_sampled_fields=sorted(extra))

def export_parquet(c,out):
    out=Path(out)
    if out.exists() and any(out.iterdir()):raise ValueError('Choose an empty Parquet output directory; never overwrite a published snapshot')
    out.parent.mkdir(parents=True,exist_ok=True)
    c.execute(f"COPY (SELECT * FROM positions_raw ORDER BY archive_date,kind,route,ts,vehicle_id) TO {quote(out.resolve())} (FORMAT PARQUET,PARTITION_BY(kind,archive_date),COMPRESSION ZSTD,ROW_GROUP_SIZE 122880)")
    manifest=dict(schema='common typed source projection; vehicle_ts is RAW',files=[dict(path=str(p.relative_to(out)),bytes=p.stat().st_size,sha256=file_hash(p)) for p in sorted(out.rglob('*.parquet'))])
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    a=sub.add_parser('ingest');a.add_argument('--db',type=Path,required=True);a.add_argument('--raw-dir',type=Path,required=True)
    a.add_argument('--index',default=INDEX);a.add_argument('--days',type=int,default=7);a.add_argument('--end');a.add_argument('--as-of');a.add_argument('--kinds',nargs='+',choices=list(SCHEMAS),default=list(SCHEMAS))
    e=sub.add_parser('export');e.add_argument('--db',type=Path,required=True);e.add_argument('--out',type=Path,required=True)
    for parser in [a,e]:parser.add_argument('--threads',type=int);parser.add_argument('--memory-limit')
    args=p.parse_args();args.db.parent.mkdir(parents=True,exist_ok=True)
    if args.action=='ingest':
        args.raw_dir.mkdir(parents=True,exist_ok=True)
        index=fetch_index(args.index,args.raw_dir);selected=select_files(index,args.end,args.days,args.kinds,args.as_of)
        (args.raw_dir/'index.pinned.json').write_text(json.dumps(index,indent=2))
        c=connect(args.db,threads=args.threads,memory_limit=args.memory_limit)
        try:
            initialize(c)
            for meta in selected:
                prior=c.execute('SELECT sha256,rows FROM archive_ingest WHERE kind=? AND archive_date=?',[meta['kind'],meta['date']]).fetchone()
                if prior and prior!=(meta['sha256'],meta['rows']):
                    raise ValueError('Published source changed; choose a new database and raw directory before rebuilding')
                path=ensure_file(meta,args.raw_dir);print(json.dumps(ingest_file(c,meta,path)),flush=True)
            c.execute('CHECKPOINT')
        finally:c.close()
    else:
        c=connect(args.db,read_only=True,threads=args.threads,memory_limit=args.memory_limit)
        try:print(json.dumps(export_parquet(c,args.out),indent=2))
        finally:c.close()

if __name__=='__main__':
    try:main()
    except Exception as exc:print(str(exc),file=sys.stderr);raise SystemExit(1)
