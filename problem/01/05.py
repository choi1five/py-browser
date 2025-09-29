# 실행 명령어: python problem/01/05.py view-source:http://example.org/

import socket
import ssl


class URL:
  def __init__(self, url):
    # view-source 스킴 처리 추가
    if url.startswith("view-source:"):
      self.view_source = True
      url = url[12:]  # "view-source:" 제거
    else:
      self.view_source = False

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

def show(body):
  # HTML 태그 제거하여 텍스트만 출력
  in_tag = False
  for c in body:
    if c == "<":
      in_tag = True
    elif c == ">":
      in_tag = False
    elif not in_tag:
      print(c, end="")

def show_source(body):
  # view-source 모드에서는 HTML 소스를 그대로 출력
  print(body, end="")

def load(url):
  body = url.request()
  # view-source 스킴인지 확인하여 다른 출력 방식 사용
  if url.view_source:
    show_source(body)
  else:
    show(body)


if __name__ == "__main__":
  import sys
  load(URL(sys.argv[1]))