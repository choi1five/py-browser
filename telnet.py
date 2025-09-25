import socket

class URL:
  def __init__(self, url):
    self.scheme, url = url.split("://", 1)
    assert self.scheme == "http"

    if "/" not in url:
      url = url + "/"
    self.host, self.url = url.split("/", 1)
    self.path = "/" + url

  def request(self):
    s = socket.socket(
      family=socket.AF_INET,
      type=socket.SOCK_STREAM,
      proto=socket.IPPROTO_TCP,
    )

    s.connect((self.host, 80))

    request = "GET {} HTTP/1.0\r\n".format(self.path)
    request += "Host: {}\r\n".format(self.host)
    request += "\r\n"

    s.send(request.encode("utf-8"))

    response = s.makefile("r", encoding="utf-8", newline="\r\n")
    statusline = response.readline()
    version, status, explanation = statusline.split(" ", 2)

    response_headers = {}
    while True:
      line = response.readline()
      if line == "\r\n": break
      header, value = line.split(":", 1)
      response_headers[header.lower()] = value.strip()

    assert "transfer-encoding" not in response_headers
    assert "content-encoding" not in response_headers

    body = response.read()
    s.close()

    return body
  
url = URL("http://example.org")
response = url.request()
print(response)