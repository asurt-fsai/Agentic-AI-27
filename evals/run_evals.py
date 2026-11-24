import argparse
import json


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


REFUSAL_PHRASES = ("not covered", "cannot confirm", "ask the organisers", "ask the organizers")


def score_case(case, answer):
    if answer is None:
        return False, "no answer given"
    text = answer.get("answer", "").lower()
    if case.get("trap"):
        ok = any(p in text for p in REFUSAL_PHRASES)
        return ok, "" if ok else "trap case: should say it cannot be confirmed"
    missing = [k for k in case.get("expected", []) if k.lower() not in text]
    if missing:
        return False, f"missing keywords: {missing}"
    src = case.get("source_id")
    if src and src not in answer.get("cited_sources", []):
        return False, f"source {src} not cited"
    return True, ""


def run(cases_path, answers_path):
    cases = load_jsonl(cases_path)
    answers = {a["id"]: a for a in load_jsonl(answers_path)}
    print(f"Cases: {len(cases)}")
    passed = 0
    failures = []
    for c in cases:
        ok, why = score_case(c, answers.get(c["id"]))
        if ok:
            passed += 1
        else:
            failures.append((c["id"], why))
    print(f"Total: {passed}/{len(cases)}")
    for case_id, why in failures:
        print(f"  FAIL {case_id}: {why}")
    return passed, len(cases)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True)
    ap.add_argument("--answers", required=True)
    args = ap.parse_args()
    run(args.cases, args.answers)
