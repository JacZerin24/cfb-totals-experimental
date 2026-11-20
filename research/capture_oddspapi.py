"""Quota-aware live OddsPapi capture; append only verified pre-kickoff quotes.

No credentials or raw API responses are logged or persisted. Fixture identifiers
remain OddsPapi IDs until a separate verified CFBD crosswalk is available.
"""
import argparse,csv,datetime as dt,json,os,sys,time,urllib.parse,urllib.request,urllib.error
from pathlib import Path
from convert_oddspapi_quotes import convert
from archive_odds import ALL

BASE="https://api.oddspapi.io/v4/"
def get(path,key,**params):
    url=BASE+path+"?"+urllib.parse.urlencode(dict(params,apiKey=key))
    req=urllib.request.Request(url,headers={"User-Agent":"cfb-totals-experimental/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=35) as response:return json.load(response)
    except urllib.error.HTTPError as e:
        raise RuntimeError("OddsPapi HTTP "+str(e.code)) from None
    except Exception:
        raise RuntimeError("OddsPapi request failed") from None

def capture(key,now=None,bookmakers=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    account=get("account",key)
    subs=account.get("subscriptions") or []
    sub=next((x for x in subs if isinstance(x,dict) and x.get("is_active")),None)
    if not sub:raise RuntimeError("No active OddsPapi subscription")
    try:remaining=int(sub["request_limit"])-int(sub["request_count"])
    except (KeyError,TypeError,ValueError):raise RuntimeError("Unknown OddsPapi quota: refusing requests")
    if remaining<15:raise RuntimeError("OddsPapi quota reserve: refusing market calls")
    allowed=sub.get("bookmakers") or {}
    allowed=set(allowed if isinstance(allowed,(list,dict)) else [])
    preferred=bookmakers or ["hardrockbet","bet365","draftkings","betrivers"]
    chosen=next((x for x in preferred if x in allowed),None)
    if not chosen:raise RuntimeError("No preferred sportsbook allowed by subscription")
    catalog=get("markets",key,language="en")
    odds=get("odds-by-tournaments",key,tournamentIds="27653",bookmakers=chosen,
             language="en",verbosity=3,oddsFormat="american")
    rows,stats=convert(catalog,odds,now.isoformat())
    stats["bookmaker"]=chosen
    stats["quota_remaining_before_market_calls"]=remaining
    return rows,stats

def append_day(rows,root):
    by_day={}
    for row in rows:
        day=row["observed_utc"][:10]
        by_day.setdefault(day,[]).append(row)
    inserted=0
    for day,new in by_day.items():
        path=root/(day+".csv")
        path.parent.mkdir(parents=True,exist_ok=True)
        existing=[]
        if path.exists():
            with path.open(newline="",encoding="utf-8") as f:existing=list(csv.DictReader(f))
        key=lambda x:tuple(x.get(c,"") for c in ALL)
        seen={key(x) for x in existing}
        for row in new:
            if key(row) not in seen:
                existing.append(row);seen.add(key(row));inserted+=1
        with path.open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=ALL);writer.writeheader();writer.writerows(existing)
    return inserted

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,default=Path("data/prospective/oddspapi"))
    a=p.parse_args()
    key=os.getenv("ODDSPAPI_API_KEY","").strip()
    if not key:
        print("ODDSPAPI_CAPTURE=skipped_missing_secret");return
    try:
        rows,stats=capture(key)
    except RuntimeError as e:
        print("ODDSPAPI_CAPTURE=unavailable; "+str(e))
        return
    inserted=append_day(rows,a.output_dir)
    # Counts only: no raw provider data, secret, or price values in CI logs.
    print("ODDSPAPI_CAPTURE="+json.dumps(dict(stats,inserted=inserted),sort_keys=True))
    if not rows:print("ODDSPAPI_CAPTURE_WARNING=no_unambiguous_quotes; no data appended")

if __name__=="__main__":main()
