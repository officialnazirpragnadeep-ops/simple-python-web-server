# Simple Web Server (HTTP)

This is a small educational HTTP server for a 5th-semester Computer Networks
project. It uses Python TCP sockets directly, without Flask, Django, or any
other web framework.

## Features

- `GET /` and `GET /about` return HTML with `200 OK`.
- An unknown path returns an HTML page with `404 Not Found`.
- Any method other than `GET` returns an HTML page with `405 Method Not Allowed`.
- The 405 response includes `Allow: GET`.
- The response includes `Content-Type`, `Content-Length`, and `Connection` headers.

## Requirements

- Python 3.10 or newer
- A web browser
- `curl` for checking the exact status line and headers

## Run the server

From this project directory:

```bash
python3 server.py
```

The server listens at `http://127.0.0.1:8080`.

Open that address in a browser. You can also open `/about` and
`/does-not-exist` from the links on the home page.

To use a different port:

```bash
python3 server.py --port 9000
```

Stop the server with `Ctrl+C`.

## Test the status codes with curl

Run these commands while the server is running:

```bash
curl -i http://127.0.0.1:8080/
```

Expected status line:

```text
HTTP/1.1 200 OK
```

```bash
curl -i http://127.0.0.1:8080/does-not-exist
```

Expected status line:

```text
HTTP/1.1 404 Not Found
```

```bash
curl -i -X POST http://127.0.0.1:8080/
```

Expected status line and header:

```text
HTTP/1.1 405 Method Not Allowed
Allow: GET
```

The `-i` option prints the response headers as well as the HTML body.

## How the server works

1. `socket.socket(AF_INET, SOCK_STREAM)` creates an IPv4 TCP socket.
2. `bind()` assigns the local IP address and port.
3. `listen()` puts the socket into listening mode.
4. `accept()` creates a new socket for each browser or curl connection.
5. `recv()` reads the HTTP request bytes.
6. The server reads the method and path from the first request line, such as
   `GET /about HTTP/1.1`.
7. The route is selected and a status code is chosen.
8. `sendall()` sends the HTTP status line, headers, and HTML body.
9. The connection is closed after one response.

Example request:

```http
GET /about HTTP/1.1
Host: 127.0.0.1:8080
Connection: close
```

Example response structure:

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: <number of bytes>
Connection: close

<!doctype html>...
```

## Mapping to the university syllabus

| Syllabus unit | Connection to this project |
|---|---|
| Unit 1: Network fundamentals | The browser and server use a client-server architecture and communicate through layered protocols. |
| Unit 3: Network layer | `127.0.0.1` is an IPv4 loopback address; the port identifies the server process on the host. |
| Unit 4: Transport layer | `SOCK_STREAM` uses TCP, which provides connection-oriented, reliable, ordered byte delivery. |
| Unit 5: Application layer | HTTP request/response messages, HTML, methods, headers, and status codes are implemented directly. |
| Unit 2: Data link layer | The TCP/IP data sent through the socket is ultimately carried by the local network interface and Ethernet/Wi-Fi frames. |

## Viva questions and short answers

### Why is TCP used here?

HTTP needs a reliable byte stream. TCP establishes a connection and ensures
that bytes arrive in order and are retransmitted when necessary.

### What is the difference between an IP address and a port?

An IP address identifies a host or interface. A port identifies a process or
service on that host. This server uses the loopback IP `127.0.0.1` and port
`8080`.

### What does `200`, `404`, and `405` mean?

- `200 OK`: the request succeeded.
- `404 Not Found`: the requested route does not exist.
- `405 Method Not Allowed`: the route/server does not support the requested
  HTTP method; this server allows only `GET`.

### What is the role of `Content-Length`?

It tells the client how many bytes belong to the response body. The server
calculates it from the UTF-8 encoded HTML body.

### Is this a production web server?

No. It is intentionally small for learning. It supports one request per
connection, has no TLS, authentication, caching, advanced HTTP parsing, or
concurrent worker pool.

## Suggested project-record structure

1. Title and objective
2. Problem statement
3. Software and hardware requirements
4. Background: TCP sockets and HTTP request/response
5. Algorithm / flowchart
6. Source code
7. Test cases and screenshots
8. Syllabus mapping
9. Limitations and future enhancements
10. Conclusion
