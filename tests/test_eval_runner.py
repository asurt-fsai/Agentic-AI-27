from evals.run_evals import run


def test_dummy_scores_and_counts():
    passed, total = run("evals/cases/dummy.jsonl", "evals/answers_dummy.jsonl")
    assert total == 2
    assert passed == 2
