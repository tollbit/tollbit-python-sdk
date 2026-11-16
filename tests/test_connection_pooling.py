import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import anyio
import pytest

from tollbit import crawl_content


@pytest.mark.parametrize("asynchronous", [False, True])
def test_crawl_batch_reuses_connection_for_tokens_and_content(monkeypatch, asynchronous):
    requests = []
    connections = []
    disconnected = threading.Event()

    class Gateway(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def setup(self):
            super().setup()
            connections.append(self.client_address)

        def finish(self):
            super().finish()
            disconnected.set()

        def do_POST(self):
            self.rfile.read(int(self.headers["Content-Length"]))
            self.respond({"token": "test-token"})

        def do_GET(self):
            self.respond(
                {
                    "metadata": {},
                    "content": {"header": "", "body": "article", "footer": ""},
                    "rate": {
                        "price": {"priceMicros": 0, "currency": "USD"},
                        "license": {
                            "id": "license-cuid",
                            "licenseType": "STANDARD",
                            "licensePath": "/licenses/standard",
                            "permissions": [],
                        },
                    },
                }
            )

        def respond(self, data):
            requests.append((self.command, self.headers.get("Cookie")))
            body = json.dumps(data).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Set-Cookie", "session=unexpected; Path=/")
            self.end_headers()
            self.wfile.write(body)

    with ThreadingHTTPServer(("127.0.0.1", 0), Gateway) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        monkeypatch.setenv(
            "TOLLBIT_SDK_DEVELOPER_API_BASE_URL", f"http://127.0.0.1:{server.server_port}"
        )
        monkeypatch.setenv("NO_PROXY", "127.0.0.1")
        url = "https://example.com/article"

        async def crawl_async():
            async with crawl_content.create_async_client("key", "agent") as client:
                for _ in range(2):
                    await client.crawl_content(url)

        try:
            if asynchronous:
                anyio.run(crawl_async)
            else:
                with crawl_content.create_client("key", "agent") as client:
                    for _ in range(2):
                        client.crawl_content(url)
            assert len(connections) == 1
            assert requests == [("POST", None), ("GET", None)] * 2
            assert disconnected.wait(timeout=2)
        finally:
            server.shutdown()
            thread.join()
