# python3 problem/01/04.py "data://text/html,&lt;div&gt;This &amp; that&lt;/div&gt;"

import socket
import ssl
import base64
import urllib.parse


class URL:
  def __init__(self, url):
    self.scheme, url = url.split("://", 1)
    assert self.scheme in ["http", "https", "file", "data"]

    # 스킴 처리
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
    elif self.scheme == "data":
      # data URL 데이터 저장
      self.data_url = url
      self.host = None
      self.port = None
      self.path = None
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

    # data 스킴 처리: URL에 포함된 데이터 직접 반환
    if self.scheme == "data":
      try:
        # data URL 형식: [<mediatype>][;base64],<data>
        if "," in self.data_url:
          header, data = self.data_url.split(",", 1)
        else:
          # 콤마가 없는 경우 빈 데이터로 처리
          return ""

        # mediatype과 인코딩 정보 파싱
        is_base64 = False
        mediatype = "text/plain"  # 기본값

        if header:
          parts = header.split(";")
          if parts[0]:  # mediatype이 있는 경우
            mediatype = parts[0]

          # base64 인코딩 확인
          if "base64" in parts:
            is_base64 = True

        # 데이터 디코딩
        if is_base64:
          # base64 디코딩
          try:
            decoded_data = base64.b64decode(data).decode('utf-8')
            return decoded_data
          except Exception as e:
            return f"Error decoding base64 data: {e}"
        else:
          # URL 디코딩 (퍼센트 인코딩 해제)
          decoded_data = urllib.parse.unquote(data)
          return decoded_data

      except Exception as e:
        return f"Error parsing data URL: {e}"

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

def decode_html_entities(text):
  """HTML 엔티티를 실제 문자로 변환"""
  # 주요 HTML 엔티티 매핑
  entities = {
    "&lt;": "<",      # Less than
    "&gt;": ">",      # Greater than
    "&amp;": "&",     # Ampersand
    "&quot;": '"',    # Double quote
    "&#39;": "'",     # Single quote (apostrophe)
    "&nbsp;": " ",    # Non-breaking space
    "&apos;": "'",    # Apostrophe (XML/XHTML)
  }

  # 엔티티를 실제 문자로 변환
  for entity, char in entities.items():
    text = text.replace(entity, char)

  return text

def show(body):
  """HTML 태그를 제거하고 엔티티를 디코딩하여 텍스트 콘텐츠만 출력"""
  in_tag = False
  text_content = ""

  # HTML 태그 제거하고 텍스트만 추출
  for c in body:
    if c == "<":
      in_tag = True
    elif c == ">":
      in_tag = False
    elif not in_tag:
      text_content += c

  # HTML 엔티티를 실제 문자로 변환
  decoded_text = decode_html_entities(text_content)

  # 출력
  print(decoded_text, end="")

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