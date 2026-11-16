"""Convert authorized OddsPapi JSON exports into prospective quote CSV.

This is intentionally offline: do not assume this repository has the production
GitHub secrets. Requires raw JSON exports of /markets and /odds-by-tournaments.
Only explicit over/under outcome keys are accepted; ambiguous labels are skipped.
"""
import argparse,csv,datetime as dt,json,math,re
from pathlib import Path
from archive_odds import ALL,validate

def records(payload):
    if isinstance(payload,list):return payload
    if isinstance(payload,dict):
        if payload.get("fixtureId"):return [payload]
        for key in ("data","odds","results","fixtures"):
            if isinstance(payload.get(key),list):return payload[key]
    return []

def convert(catalog,odds,observed_utc):
    lookup={str(x.get("marketId")):x for x in records(catalog) if isinstance(x,dict)}
    rows=[];stats=dict(fixtures=0,markets=0,ambiguous_outcomes=0,invalid=0,accepted=0)
    for fixture in records(odds):
        if not isinstance(fixture,dict):continue
        stats["fixtures"]+=1
        fixture_id=str(fixture.get("fixtureId") or "")
        kickoff=fixture.get("startTime")
        if not fixture_id or not kickoff:continue
        for book_name,book in (fixture.get("bookmakerOdds") or {}).items():
            if not isinstance(book,dict) or book.get("bookmakerIsActive") is False or book.get("suspended") is True:continue
            for market_id,market in (book.get("markets") or {}).items():
                info=lookup.get(str(market_id),{})
                if not isinstance(market,dict) or market.get("marketActive") is False:continue
                if str(info.get("marketType","")).lower()!="totals":continue
                if str(info.get("period","")).lower() not in ("result","fulltime","full_time","game","match"):continue
                if info.get("playerProp") or "team" in str(info.get("marketName","")).lower():continue
                try:line=float(info.get("handicap"))
                except (ValueError,TypeError):continue
                if not 20<=line<=100:continue
                stats["markets"]+=1
                for outcome_key,outcome in (market.get("outcomes") or {}).items():
                    # No inferred sides from arbitrary ordering or market naming.
                    label=str(outcome_key).strip().lower()
                    if label not in ("over","under"):
                        stats["ambiguous_outcomes"]+=1;continue
                    if not isinstance(outcome,dict):continue
                    players=outcome.get("players") or {}
                    node=players.get("0") if isinstance(players,dict) else None
                    if not isinstance(node,dict) or node.get("active") is not True:continue
                    try:
                        price=float(node.get("price"))
                        if not math.isfinite(price):continue
                    except (ValueError,TypeError):continue
                    row=dict(source="OddsPapi",source_quote_id=f"{fixture_id}:{book_name}:{market_id}:{label}",
                             observed_utc=observed_utc,bookmaker=str(book_name),game_id=fixture_id,
                             kickoff_utc=kickoff,market="game_total",side=label,line=str(line),
                             american_odds=str(price),provider_quote_utc="",
                             home_team=str(fixture.get("participant1Name") or ""),
                             away_team=str(fixture.get("participant2Name") or ""))
                    try:rows.append(validate(row))
                    except (ValueError,OverflowError):stats["invalid"]+=1
    stats["accepted"]=len(rows)
    return rows,stats

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--markets",required=True,type=Path)
    p.add_argument("--odds",required=True,type=Path)
    p.add_argument("--observed-utc",required=True)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    with a.markets.open() as f:markets=json.load(f)
    with a.odds.open() as f:odds=json.load(f)
    rows,stats=convert(markets,odds,a.observed_utc)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=ALL);writer.writeheader();writer.writerows(rows)
    print(json.dumps(stats,sort_keys=True))
    if not rows:raise SystemExit("No unambiguous pre-kickoff priced outcomes; inspect schema before ingestion")

if __name__=="__main__":main()
