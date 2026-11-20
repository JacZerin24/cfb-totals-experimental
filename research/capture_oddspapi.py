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

def append_encrypted(rows,root,secret):
    """Encrypt complete append-only daily CSV; public repo never receives plaintext."""
    import base64,hashlib,secrets,io
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    key=hashlib.sha256(secret.encode("utf-8")).digest()
    aes=AESGCM(key)
    by_day={}
    for row in rows:by_day.setdefault(row["observed_utc"][:10],[]).append(row)
    inserted=0
    for day,new in by_day.items():
        path=root/(day+".enc")
        path.parent.mkdir(parents=True,exist_ok=True)
        existing=[]
        if path.exists():
            blob=base64.b64decode(path.read_bytes())
            plaintext=aes.decrypt(blob[:12],blob[12:],day.encode("ascii")).decode("utf-8")
            existing=list(csv.DictReader(io.StringIO(plaintext)))
        identity=lambda x:tuple(x.get(c,"") for c in ALL)
        seen={identity(x) for x in existing}
        for row in new:
            if identity(row) not in seen:
                existing.append(row);seen.add(identity(row));inserted+=1
        stream=io.StringIO()
        writer=csv.DictWriter(stream,fieldnames=ALL);writer.writeheader();writer.writerows(existing)
        nonce=secrets.token_bytes(12)
        ciphertext=aes.encrypt(nonce,stream.getvalue().encode("utf-8"),day.encode("ascii"))
        path.write_bytes(base64.b64encode(nonce+ciphertext))
    return inserted

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",type=Path,default=Path("data/prospective/oddspapi"))
    a=p.parse_args()
    key=os.getenv("ODDSPAPI_API_KEY","").strip()
    if not key:
        print("ODDSPAPI_CAPTURE=skipped_missing_secret");return
    secret=os.getenv("ODDS_ARCHIVE_ENCRYPTION_KEY","").strip()
    if not secret:
        print("ODDSPAPI_CAPTURE=skipped_missing_archive_encryption_key");return
    try:
        rows,stats=capture(key)
    except RuntimeError as e:
        print("ODDSPAPI_CAPTURE=unavailable; "+str(e))
        return
    inserted=append_encrypted(rows,a.output_dir,secret)
    # Counts only: no raw provider data, secret, or price values in CI logs.
    print("ODDSPAPI_CAPTURE="+json.dumps(dict(stats,inserted=inserted),sort_keys=True))
    if not rows:print("ODDSPAPI_CAPTURE_WARNING=no_unambiguous_quotes; no data appended")

if __name__=="__main__":main()
