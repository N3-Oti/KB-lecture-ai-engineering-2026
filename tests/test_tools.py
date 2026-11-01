"""ツールのテスト（LLMもAPIキーも使わない）。"""

import json

from app import tools


def test_glossary_ids_are_unique_and_related_links_exist():
    terms = tools.load_glossary()
    ids = [t["id"] for t in terms]
    assert len(ids) == len(set(ids))
    for t in terms:
        for r in t["related"]:
            assert r in ids, f"{t['id']} の related に存在しない id: {r}"


def test_search_finds_term_by_name_and_alias():
    for query in ["LoRA", "lora", "Low-Rank Adaptation"]:
        hits = json.loads(tools.search_glossary(query))
        assert hits[0]["term"] == "LoRA", query


def test_search_finds_course_specific_term():
    hits = json.loads(tools.search_glossary("lecNN-start"))
    assert hits[0]["term"] == "lecNN-start タグ"


def test_search_limits_number_of_results():
    hits = json.loads(tools.search_glossary("エージェント"))
    assert 1 <= len(hits) <= tools.MAX_RESULTS


def test_search_reports_not_found():
    assert "見つかりませんでした" in tools.search_glossary("存在しない用語xyz")


def test_lecture_summary():
    assert "エージェント" in tools.get_lecture_summary(3)
    assert "まだありません" in tools.get_lecture_summary(99)


def test_make_quiz_asks_for_term_from_definition(monkeypatch):
    terms = tools.load_glossary()
    peft = next(entry for entry in terms if entry["id"] == "peft")
    selected_from = []

    def choose(candidates):
        selected_from.extend(candidates)
        return peft

    monkeypatch.setattr(tools.random, "choice", choose)

    quiz = json.loads(tools.make_quiz(2))

    assert selected_from
    assert all(entry["lecture"] == 2 for entry in selected_from)
    assert quiz["question"] == f"次の説明に当てはまる用語は何ですか？\n{peft['definition']}"
    assert quiz["answer"] == "PEFT"
    assert quiz["term_id"] == "peft"
    assert quiz["lecture"] == 2
    assert quiz["category"] == peft["category"]


def test_make_quiz_reports_when_lecture_has_no_terms(monkeypatch):
    glossary = tools.load_glossary()
    monkeypatch.setattr(tools, "load_glossary", lambda: glossary)

    result = tools.make_quiz(99)

    assert "第99回" in result
    assert "見つかりませんでした" in result
    assert "1, 2, 3, 5" in result


def test_default_question_of_lecture1_is_answerable_from_glossary():
    """第1回の既定の質問（app.ask）は、第3回のエージェントが用語集で正しく答えられること。"""
    from app.ask import DEFAULT_QUESTION

    assert "3レベル" in DEFAULT_QUESTION
    hits = json.loads(tools.search_glossary("3レベル"))
    assert hits[0]["term"] == "宿題の3レベル"
