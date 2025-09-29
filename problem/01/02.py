# python3 problem/01/02.py "file://some/directory/index.html"

import socket
import ssl


class URL:
  def __init__(self, url):
    self.scheme, url = url.split("://", 1)
    assert self.scheme in ["http", "https", "file"]

    # HTTP/HTTPS 스킴 처리
    if self.scheme == "http":
      self.port = 80
    elif self.scheme == "https":
      self.port = 443
    elif self.scheme == "file":
      # 상대 경로를 절대 경로로 변환
      if not url.startswith("/"):
        import os
        self.path = os.path.abspath(url)
      else:
        self.path = url
      self.host = None
      self.port = None
      return

    if "/" not in url:
      url = url + "/"
    self.host, url = url.split("/", 1)
    self.path = "/" + url

    if ":" in self.host:
      self.host, port = self.host.split(":", 1)
      self.port = int(port)

  def request(self):
    # file 스킴 처리: 로컬 파일 읽기
    if self.scheme == "file":
      try:
        with open(self.path, 'r', encoding='utf-8') as f:
          return f.read()
      except FileNotFoundError:
        return f"Error: File not found: {self.path}"
      except Exception as e:
        return f"Error reading file: {e}"

    # HTTP/HTTPS 요청 처리 (기존 코드)
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
    # HTTP 응답 상태라인 파싱 (사용하지 않지만 파싱은 필요)
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

  # URL이 제공되지 않은 경우 기본 파일 로드
  if len(sys.argv) == 1:
    default_url = "file://some/directory/index.html"
    load(URL(default_url))
  else:
    load(URL(sys.argv[1]))