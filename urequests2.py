import usocket
import ujson as j

def request(
    method,
    url,
    data=None,
    json=None,
    headers={},
    stream=None,
    auth=None,
    timeout=None,
    parse_headers=True,
):
    redirect = None  # redirection url, None means no redirection
    chunked_data = data and getattr(data, "__iter__", None) and not getattr(data, "__len__", None)

    if auth is not None:
        import ubinascii

        username, password = auth
        formated = b"{}:{}".format(username, password)
        formated = str(ubinascii.b2a_base64(formated)[:-1], "ascii")
        headers["Authorization"] = "Basic {}".format(formated)

    try:
        proto, dummy, host, path = url.split("/", 3)
    except ValueError:
        proto, dummy, host = url.split("/", 2)
        path = ""
    if proto == "http:":
        port = 80
    elif proto == "https:":
        import ussl

        port = 443
    else:
        raise ValueError("Unsupported protocol: " + proto)

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
    ai = ai[0]

    resp_d = None
    if parse_headers is not False:
        resp_d = {}

    s = usocket.socket(ai[0], usocket.SOCK_STREAM, ai[2])

    if timeout is not None:
        # Note: settimeout is not supported on all platforms, will raise
        # an AttributeError if not available.
        s.settimeout(timeout)

    try:
        s.connect(ai[-1])
        if proto == "https:":
            s = ussl.wrap_socket(s, server_hostname=host)
        s.write(b"%s /%s HTTP/1.1\r\n" % (method, path))
        if not "Host" in headers:
            s.write(b"Host: %s\r\n" % host)
        # Iterate over keys to avoid tuple alloc
        for k in headers:
            s.write(k)
            s.write(b": ")
            s.write(headers[k])
            s.write(b"\r\n")
        if json is not None:
            assert data is None
            import ujson

            data = ujson.dumps(json)
            s.write(b"Content-Type: application/json\r\n")
        if data:
            if chunked_data:
                s.write(b"Transfer-Encoding: chunked\r\n")
            else:
                s.write(b"Content-Length: %d\r\n" % len(data))
        s.write(b"Connection: close\r\n\r\n")
        if data:
            if chunked_data:
                for chunk in data:
                    s.write(b"%x\r\n" % len(chunk))
                    s.write(chunk)
                    s.write(b"\r\n")
                s.write("0\r\n\r\n")
            else:
                s.write(data)

        l = s.readline()
        l = l.split(None, 2)
        if len(l) < 2:
            # Invalid response
            raise ValueError("HTTP error: BadStatusLine:\n%s" % l)
        status = int(l[1])
        reason = ""
        if len(l) > 2:
            reason = l[2].rstrip()
        out = b''

        # specifically adapted to extract response from BART API
        while True:
            l = s.readline()
            if l.startswith(b'{"?xml":'):
                break
        s.close()
        
        return j.loads(l.decode("utf-8").replace("HTTP/1.1 400 Bad Request\r\n", ""))
    except OSError:
        s.close()
        raise
