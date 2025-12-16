# --- Mocks and Fixtures ---
class MockResponse:
    def __init__(self, json_obj=None, problem_json_obj=None, body_text=None, status_code=200):
        self._json_obj = json_obj or []
        self._problem_json_obj = problem_json_obj or []
        self.body_text = body_text
        self.status_code = status_code

    def json(self):
        return self._json_obj or self._problem_json_obj

    @property
    def text(self):
        return self.body_text

    @property
    def headers(self):
        if self._problem_json_obj is not None:
            return {"Content-Type": "application/problem+json"}
        elif self._json_obj is not None:
            return {"Content-Type": "application/json"}
        else:
            return {"Content-Type": "text/plain"}

    @property
    def reason(self):
        return self.body_text or "OK"
