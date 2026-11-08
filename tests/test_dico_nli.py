import importlib
import math
import sys

import pytest

from dico_nli import data, llm
from dico_nli.baselines import length_rule, rule_baselines, structure_report
from dico_nli.decoding import DECODINGS, decode
from dico_nli.labels import BE, EQ, FE, LABELS, NO, REV, is_consistent
from dico_nli.metrics import score

needs_data = pytest.mark.skipif(
    not data.path("dev", 1).exists(), reason="dati non scaricati: scripts/download_data.py")


def _rows(pairs):
    """Righe reference minime: [(gold originale, gold invertita)] -> righe con reverse_pair_id."""
    rows = []
    for i, (go, gf) in enumerate(pairs):
        o, f = f"p{i}__en-en__original", f"p{i}__en-en__flipped"
        rows += [{"instance_id": o, "reverse_pair_id": f, "label": go},
                 {"instance_id": f, "reverse_pair_id": o, "label": gf}]
    return rows


def test_reverse_map_is_involution():
    assert all(REV[REV[l]] == l for l in REV)
    assert NO not in REV
    assert is_consistent(FE, BE) and is_consistent(EQ, EQ)
    assert not is_consistent(NO, NO) and not is_consistent(BE, EQ)


def test_reverse_id_also_for_mixed_track():
    assert data.reverse_id("dico_phrasis_0000002__en-es__flipped") == "dico_phrasis_0000002__es-en__original"
    assert data.reverse_id("x__eu-eu__original") == "x__eu-eu__flipped"


@pytest.mark.parametrize("po,pf,soft,hard", [
    (BE, FE, 1, 1),   # entrambe giuste e compatibili
    (FE, BE, 1, 0),   # compatibili ma sbagliate
    (BE, EQ, 0, 0),   # una giusta, incompatibili
    (EQ, EQ, 1, 0),   # costante: compatibile, sbagliata
    (NO, NO, 0, 0),   # (NO, NO) non conta come coerente
])
def test_consistency_metrics_table(po, pf, soft, hard):
    # tabella della sezione 2 di dico-nli-claude-e-obiettivi.md: gold (BE, FE)
    rows = _rows([(BE, FE)])
    m = score(rows, {rows[0]["instance_id"]: po, rows[1]["instance_id"]: pf})
    assert (m["SoftCons"], m["HardCons"]) == (soft, hard)


def test_weighted_f1_perfect_and_singletons_ignored_by_consistency():
    rows = _rows([(FE, BE), (EQ, EQ)]) + [{"instance_id": "q__en-en__original", "reverse_pair_id": "",
                                            "label": NO}]
    m = score(rows, {r["instance_id"]: r["label"] for r in rows})
    assert m == {"wF1": 1.0, "SoftCons": 1.0, "HardCons": 1.0}


def test_decode_inversion_numeric_example():
    # esempio numerico della sezione 3: indipendente (BE, EQ), vincolata (BE, FE)
    o, f = "p__en-en__original", "p__en-en__flipped"
    lp = {o: [math.log(x) for x in (0.30, 0.10, 0.55, 0.05)],
          f: [math.log(x) for x in (0.50, 0.40, 0.05, 0.05)]}
    assert decode([o, f], lp, **DECODINGS["indipendente"]) == {o: BE, f: EQ}
    assert decode([o, f], lp, **DECODINGS["+ inversione"]) == {o: BE, f: FE}


def test_decode_crosslingual_and_leak():
    lp_en = [math.log(x) for x in (0.4, 0.5, 0.05, 0.05)]
    lp_eu = [math.log(x) for x in (0.9, 0.05, 0.03, 0.02)]
    ids = ["p__en-en__original", "p__eu-eu__original", "s__en-en__original"]
    lp = {ids[0]: lp_en, ids[1]: lp_eu, ids[2]: lp_en}
    out = decode(ids, lp, **DECODINGS["+ cross-lingue"])
    assert out[ids[0]] == out[ids[1]] == EQ  # il basco, piu' sicuro, trascina l'inglese
    out = decode(ids, lp, inversion=True, crossling=True, leak=True)
    assert out[ids[2]] == NO  # nessuna inversa nel file


def test_length_rule():
    assert length_rule({"text1": "war shrine visit", "text2": "shrine visit"}) == FE
    assert length_rule({"text1": "a b", "text2": "c d"}) == EQ


def test_llm_schema_and_parse():
    assert llm.SCHEMA["properties"]["label"]["enum"] == list(LABELS)
    raw = [{"id": "a", "type": "succeeded", "stop_reason": "end_turn",
            "text": '{"label": "EQUIVALENCE", "probabilities": {"EQUIVALENCE": 0.7, '
                    '"FORWARD_ENTAILMENT": 0.1, "BACKWARD_ENTAILMENT": 0.1, "NEGATIVE_OTHER": 0.1}}'},
           {"id": "b", "type": "succeeded", "stop_reason": "refusal", "text": ""},
           {"id": "c", "type": "errored"}]
    labels, logp, missing = llm.parse(raw)
    assert labels["a"] == EQ and missing == ["b", "c"]
    assert abs(sum(math.exp(x) for x in logp["a"]) - 1) < 1e-9


def test_request_params_shape():
    p = llm.request_params({"text1": "a", "text2": "b"}, "sys", llm.MODEL, "high")
    assert p["thinking"] == {"type": "adaptive"}
    assert p["output_config"]["effort"] == "high"
    assert "fallbacks" not in p  # non accettato dalla Batches API


@needs_data
def test_dataset_shape_parallel_tracks_and_artifact():
    for split, n in (("train", 3042), ("dev", 660)):
        tr = {t: data.load(split, t) for t in (1, 2, 3)}
        assert all(len(v) == n for v in tr.values())
        lab = [{(r["pair_id"], r["direction"]): r["label"] for r in tr[t]} for t in (1, 2, 3)]
        assert lab[0] == lab[1] == lab[2]  # traduzioni parallele
        s = structure_report(tr[1])
        assert s["acc_pair_id_singolo"] == 1.0
    assert len(data.load("train", 4)) == 18252 and len(data.load("dev", 4)) == 3960


@needs_data
def test_rule_baselines_match_september():
    m = rule_baselines(data.load("dev", 1))
    assert round(m["costante EQUIVALENCE"]["wF1"], 3) == 0.110
    assert round(m["regola lunghezza"]["wF1"], 3) == 0.467
    assert round(m["regola lunghezza"]["HardCons"], 3) == 0.614
    assert round(m["regola lunghezza + struttura"]["wF1"], 3) == 0.667


@needs_data
def test_metrics_match_official_scorer():
    """Confronto con evaluation_functions del repository ufficiale, se scaricato."""
    if not (data.RAW / "evaluation_functions" / "metrics.py").exists():
        pytest.skip("scorer ufficiale non scaricato")
    sys.path.insert(0, str(data.RAW))
    try:
        io = importlib.import_module("evaluation_functions.io")
        val = importlib.import_module("evaluation_functions.validation")
        met = importlib.import_module("evaluation_functions.metrics")
    finally:
        sys.path.pop(0)
    for track in (1, 4):
        gold = val.validate_reference_records(io.read_reference_file(data.path("dev", track)))
        rows = data.load("dev", track)
        # predizione deliberatamente imperfetta: regola di lunghezza
        pred = {r["instance_id"]: length_rule(r) for r in rows}
        official = met.compute_evaluation(gold, pred)
        ours = score(rows, pred)
        assert ours["wF1"] == pytest.approx(official.weighted_f1)
        assert ours["SoftCons"] == pytest.approx(official.soft_cons)
        assert ours["HardCons"] == pytest.approx(official.hard_cons)
