# -*- coding: utf-8 -*-
import csv
from datetime import datetime

INPUT_CSV  = "shifts.csv"             # 元のシフト
TRACE_CSV  = "選考過程.csv"            # 選考プロセス
OUTPUT_CSV = "更新後シフト.csv"        # 補充後のシフト

DTFMT = "%Y-%m-%d %H:%M"

def parse_dt(s):
    return datetime.strptime(s.strip(), DTFMT)

def overlap(a_start, a_end, b_start, b_end):
    return max(a_start, b_start) < min(a_end, b_end)

def load_shifts(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows

def total_hours_for(helper, rows):
    total = 0.0
    for r in rows:
        if r["helper"] == helper:
            try:
                h = (parse_dt(r["end"]) - parse_dt(r["start"])).total_seconds()/3600.0
            except Exception:
                h = 0.0
            total += max(0.0, h)
    return total

def main():
    rows = load_shifts(INPUT_CSV)

    print("=== シフトキャンセル → 自動補充 DEMO ===")
    print("\n現在のシフト（番号｜ヘルパー｜利用者｜タスク｜開始→終了）:")
    for i, r in enumerate(rows):
        print(f"{i:02d}｜{r['helper']}｜{r['user']}｜{r['task']}｜{r['start']}→{r['end']}")

    # キャンセル対象を選択
    while True:
        idx_s = input("\nキャンセルされたシフトの【番号】を入力してください（Enterで0番）: ").strip()
        if idx_s == "":
            idx = 0
            break
        if idx_s.isdigit() and 0 <= int(idx_s) < len(rows):
            idx = int(idx_s)
            break
        print("番号が正しくありません。もう一度入力してください。")

    cancel_row = rows[idx]
    c_helper = cancel_row["helper"]
    c_start  = parse_dt(cancel_row["start"])
    c_end    = parse_dt(cancel_row["end"])
    print(f"\n☎️ システム検知：{c_helper} のシフトがキャンセルされました → {cancel_row['start']}→{cancel_row['end']}（{cancel_row['task']}）")

    helpers = sorted(set(r["helper"] for r in rows))
    candidates = [h for h in helpers if h != c_helper]

    trace = []
    for h in candidates:
        conflicts = []
        for r in rows:
            if r["helper"] != h:
                continue
            try:
                s = parse_dt(r["start"]); e = parse_dt(r["end"])
            except Exception:
                continue
            if overlap(c_start, c_end, s, e):
                conflicts.append(f"{r['start']}→{r['end']}（{r['task']}）")

        eligible = (len(conflicts) == 0)
        hours = total_hours_for(h, rows)
        base = 100 if eligible else 0
        workload_component = max(0.0, 30.0 * (1.0 - min(hours, 40.0)/40.0))
        score = base + workload_component

        reasons = []
        if eligible:
            reasons.append("時間重複なし:+100")
        else:
            reasons.append(f"時間重複あり({len(conflicts)}件):0")
        reasons.append(f"現在の総労働時間 {hours:.1f}h:+{workload_component:.1f}")

        trace.append({
            "ヘルパー": h,
            "補充可能": "はい" if eligible else "いいえ",
            "選ばれた": "",
            "総労働時間(h)": f"{hours:.1f}",
            "スコア": f"{score:.1f}",
            "重複シフト": " / ".join(conflicts) if conflicts else "",
            "理由": "; ".join(reasons)
        })

    # スコア順に並べる
    trace.sort(key=lambda x: (x["補充可能"] != "はい", -float(x["スコア"])))

    chosen = None
    for t in trace:
        if t["補充可能"] == "はい":
            t["選ばれた"] = "はい"
            chosen = t["ヘルパー"]
            break
    for t in trace:
        if t["選ばれた"] == "":
            t["選ばれた"] = "いいえ"

    with open(TRACE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "ヘルパー","補充可能","選ばれた","総労働時間(h)","スコア","重複シフト","理由"
        ])
        writer.writeheader()
        writer.writerows(trace)

    if chosen:
        print(f"\n✅ 補充者：{chosen}")
        updated = [dict(r) for r in rows]
        updated[idx]["helper"] = chosen
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["helper","user","task","start","end"])
            writer.writeheader()
            writer.writerows(updated)
        print(f"📄 {TRACE_CSV}（選考過程）と {OUTPUT_CSV}（補充後シフト）を生成しました。")
    else:
        print("\n⚠️ 補充可能なヘルパーが見つかりませんでした。")
        print(f"📄 {TRACE_CSV} に選考過程を記録しました。")

if __name__ == "__main__":
    main()
