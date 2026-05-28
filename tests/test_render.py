from src.render import print_json_result, print_text_result


def test_print_json_result_emits_values(capsys):
    print_json_result({"state": "STABLE", "confidence": "High"})
    out = capsys.readouterr().out
    assert "STABLE" in out and "High" in out


def test_print_text_result_emits_text_literally(capsys):
    print_text_result("<IDENT>Dr. X</IDENT> on lithium")
    out = capsys.readouterr().out
    assert "IDENT" in out and "lithium" in out
