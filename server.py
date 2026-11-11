import argparse
import html
import socket
from pathlib import Path
from urllib.parse import urlsplit


HOST = "127.0.0.1"
PORT = 8080
WEB_FOLDER = Path(__file__).resolve().parent / "web"

PAGES = {
    "/": WEB_FOLDER / "index.html",
    "/about": WEB_FOLDER / "about.html",
}

STATUS_TEXT = {
    200: "OK",
    400: "Bad Request",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
}


def error_page(title, heading, message):
    title = html.escape(title)
    heading = html.escape(heading)
    message = html.escape(message)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
</head>
<body>
    <h1>{heading}</h1>
    <p>{message}</p>
</body>
</html>
"""


def make_response(status_code, body, extra_headers=None):
    body = body.encode("utf-8")
    reason = STATUS_TEXT[status_code]

    headers = {
        "Content-Type": "text/html; charset=utf-8",
        "Content-Length": str(len(body)),
        "Connection": "close",
    }

    if extra_headers:
        headers.update(extra_headers)

    response = f"HTTP/1.1 {status_code} {reason}\r\n"

    for name, value in headers.items():
        response += f"{name}: {value}\r\n"

    return (response + "\r\n").encode("iso-8859-1") + body


def send_page(client, status_code, body, headers=None):
    client.sendall(make_response(status_code, body, headers))


def handle_client(client, address):
    client.settimeout(5)

    try:
        data = client.recv(4096)

        if not data:
            return

        request = data.decode("iso-8859-1")
        request_line = request.split("\r\n", 1)[0]
        parts = request_line.split()

        if len(parts) != 3:
            body = error_page(
                "400 Bad Request",
                "400 - Bad Request",
                "The request could not be understood.",
            )

            send_page(client, 400, body)
            print(f"{address} -> 400")
            return

        method, target, _ = parts
        path = urlsplit(target).path or "/"

        if method != "GET":
            body = error_page(
                "405 Method Not Allowed",
                "405 - Method Not Allowed",
                f"The method {method} is not supported. Try GET {path} instead.",
            )

            send_page(client, 405, body, {"Allow": "GET"})
            print(f"{address} -> 405 {method} {path}")
            return

        page = PAGES.get(path)

        if page is None:
            body = error_page(
                "404 Not Found",
                "404 - Page Not Found",
                f"There is no page registered for {path}.",
            )

            send_page(client, 404, body)
            print(f"{address} -> 404 GET {path}")
            return

        try:
            body = page.read_text(encoding="utf-8")

        except OSError:
            body = error_page(
                "500 Internal Server Error",
                "500 - Internal Server Error",
                "The requested HTML file could not be read.",
            )

            send_page(client, 500, body)
            print(f"{address} -> 500 GET {path}")
            return

        send_page(client, 200, body)
        print(f"{address} -> 200 GET {path}")

    except (ConnectionResetError, socket.timeout):
        print(f"{address} -> connection closed")


def run_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(5)

        print(f"Serving {WEB_FOLDER} at http://{host}:{port}")
        print("Press Ctrl+C to stop the server.")

        try:
            while True:
                client, address = server.accept()

                with client:
                    handle_client(client, address)

        except KeyboardInterrupt:
            print("\nServer stopped.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", type=int, default=PORT)

    args = parser.parse_args()
    run_server(args.host, args.port)


if __name__ == "__main__":
    main()