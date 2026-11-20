"""Offline unit checks for optional independent-review API adapter."""
import api_review
import taskctl


def run():
    assert api_review.DEFAULT_MODEL == "gpt-6.2-astra"
    p = api_review.request_payload("gpt-6.2-astra", "Review input")
    assert p["store"] is False and p["text"]["format"]["strict"] is True
    try:
        api_review.request_payload("bad model\n", "x")
    except taskctl.GateError:
        pass
    else:
        raise AssertionError("Unsupported model argument accepted")
    expected = {"verdict": "approved", "summary": "No blocking finding", "findings": []}
    fake = {"id": "resp_valid_fixture", "status": "completed", "output": [
        {"content": [{"type": "output_text", "text": __import__('json').dumps(expected)}]}]}
    assert api_review.parse_response(fake) == expected
    fake["id"] = ""
    try:
        api_review.parse_response(fake)
    except taskctl.GateError:
        pass
    else:
        raise AssertionError("Blank provider session accepted")
    fake["id"] = "resp_valid_fixture"
    fake["output"][0]["content"][0]["text"] = __import__('json').dumps({
        "verdict": "approved", "summary": "bad", "findings": [{
            "id": "F1", "severity": "high", "location": "x.py:1", "title": "issue", "detail": "bad", "fix": "fix"}]})
    try:
        api_review.parse_response(fake)
    except taskctl.GateError:
        pass
    else:
        raise AssertionError("Contradictory approval accepted")
    return {"api_adapter_self_test": "passed", "live_API_called": False}


if __name__ == "__main__":
    print(run())