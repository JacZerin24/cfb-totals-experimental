"""Historical HGB weather ablation (diagnostic, not exact original replication).

Usage: python research/weather_ablation.py data/external/cfb-live-training-data/modeling_dataset.csv
Dependencies: pandas, numpy, scikit-learn. Results depend on sklearn version.
Original published audit used sklearn 1.9; the first diagnostic was run with 1.8.
"""
from __future__ import annotations
import argparse
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import HistGradientBoostingRegressor

WEATHER_NUM = {"wind_mph","temperature_f","humidity","precipitation","snowfall","dewpoint_f","pressure"}
WEATHER_CAT = {"wind_bin","temp_bin"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset")
    parser.add_argument("--output", default="reports/generated_weather_ablation.csv")
    args = parser.parse_args()
    df = pd.read_csv(args.dataset, low_memory=False).dropna(subset=["closing_total","actual_total_points","season"]).copy()
    df["game_indoors_bool"] = df.game_indoors.astype(str).str.lower().isin(["true","1","yes"])
    df["fbs_vs_fbs"] = df.home_classification.eq("fbs") & df.away_classification.eq("fbs")
    df["total_bin"] = pd.cut(df.closing_total, [0,42,49,56,63,100], labels=["<=42","42-49","49-56","56-63","63+"])
    df["market_residual"] = df.actual_total_points - df.closing_total
    base = ["closing_total","wind_mph","temperature_f","humidity","precipitation","snowfall","dewpoint_f","pressure","home_pregame_elo","away_pregame_elo"]
    prior = [c for c in df if c.startswith(("home_prior_","away_prior_"))]
    nums = [c for c in base + prior if pd.to_numeric(df[c], errors="coerce").notna().any()]
    cats = [c for c in ["game_indoors_bool","neutral_site","conference_game","line_provider","wind_bin","temp_bin","total_bin","fbs_vs_fbs","home_conference","away_conference"] if c in df]
    for c in cats:
        df[c] = df[c].astype(str).fillna("missing")
    results = []
    for regime in ("published_style", "no_observed_weather"):
        ns = nums if regime == "published_style" else [c for c in nums if c not in WEATHER_NUM]
        cs = cats if regime == "published_style" else [c for c in cats if c not in WEATHER_CAT]
        prep = ColumnTransformer([
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")),("scale",StandardScaler())]), ns),
            ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore"))]), cs),
        ])
        model = Pipeline([("prep", prep),("model",HistGradientBoostingRegressor(max_iter=250,learning_rate=.04,l2_regularization=.5,min_samples_leaf=35,random_state=42,early_stopping=False))])
        for season in sorted(df.season.unique()):
            train = df[df.season < season]
            test = df[df.season == season]
            if len(train) < 1000 or len(test) < 100:
                continue
            model.fit(train[ns+cs], train.market_residual)
            pred = model.predict(test[ns+cs])
            fbs = test.home_classification.eq("fbs") & test.away_classification.eq("fbs")
            mask = fbs.to_numpy() & (test.closing_total.to_numpy() >= 56) & (pred <= -4)
            selected = test.iloc[np.flatnonzero(mask)]
            w = int((selected.actual_total_points < selected.closing_total).sum())
            l = int((selected.actual_total_points > selected.closing_total).sum())
            p = int((selected.actual_total_points == selected.closing_total).sum())
            results.append({"regime":regime,"season":int(season),"games":len(selected),"wins":w,"losses":l,"pushes":p,"roi":(w*100/110-l)/(w+l) if w+l else np.nan})
    result = pd.DataFrame(results)
    result.to_csv(args.output, index=False)
    print(result.to_string(index=False))
    print("Diagnostic only: historical quote availability unverified; model version differences may change selections.")


if __name__ == "__main__":
    main()
