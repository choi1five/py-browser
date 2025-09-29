import socket
import ssl


class URL:
  def __init__(self, url):
    self.scheme, url = url.split("://", 1)
    assert self.scheme in ["http", "https"]

    if self.scheme == "http":
      self.port = 80
    elif self.scheme == "https":
      self.port = 443

    if "/" not in url:
      url = url + "/"
    self.host, self.url = url.split("/", 1)
    self.path = "/" + self.url

    if ":" in self.host:
      self.host, port = self.host.split(":", 1)
      self.port = int(port)

  def request(self):
    s = socket.socket(
      family=socket.AF_INET,
      type=socket.SOCK_STREAM,
      proto=socket.IPPROTO_TCP,
    )

    s.connect((self.host, self.port))
    if self.scheme == "https":
      ctx = ssl.create_default_context()
      s = ctx.wrap_socket(s, server_hostname=self.host)

    # HTTP/1.1으로 변경하고 필요한 헤더들 추가
    request = "GET {} HTTP/1.1\r\n".format(self.path)  # HTTP/1.0 → HTTP/1.1로 변경
    request += "Host: {}\r\n".format(self.host)         # 기존 Host 헤더 유지
    request += "Connection: close\r\n"                  # 추가: Connection 헤더 (close 값)
    request += "User-Agent: PythonBrowser/1.0\r\n"  # 추가: User-Agent 헤더
    request += "\r\n"

    # 요청 내용 확인을 위해 출력
    print("=== 전송하는 HTTP 요청 ===")
    print(repr(request))
    print("=== 요청 내용 (개행 적용) ===")
    print(request.replace('\r\n', '\n'), end="")
    print("======================")

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

def show(body):
  in_tag = False
  for c in body:
    if c == "<":
      in_tag = True
    elif c == ">":
      in_tag = False
    elif not in_tag:
      print(c, end="")

def load(url):
  body = url.request()
  show(body)


if __name__ == "__main__":
  import sys
  load(URL(sys.argv[1]))