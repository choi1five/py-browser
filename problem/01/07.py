# 실행 명령어: python3 problem/01/07.py http://browser.engineering/redirect

# [리다이렉트 처리 수도코드]
#
# def request(redirect_count=0):
#     # 1. 리다이렉트 루프 방지
#     if redirect_count >= MAX_REDIRECTS:
#         raise Exception("Too many redirects")
#
#     # 2. HTTP 요청 수행
#     socket 연결 → HTTP 요청 전송 → 응답 수신
#
#     # 3. 응답 헤더 파싱
#     statusline 파싱 (version, status, explanation)
#     response_headers 수집
#
#     # 4. 리다이렉트 처리 (300번대 상태 코드)
#     if status가 "3"으로 시작:
#         if "location" 헤더 존재:
#             # 4-1. 전체 URL (http:// 또는 https://)
#             if location이 절대 URL:
#                 new_url = URL(location)
#                 return new_url.request(redirect_count + 1)  # 재귀 호출
#
#             # 4-2. 상대 경로
#             else:
#                 현재 scheme, host, port 유지
#                 새로운 경로로 URL 생성
#                 return new_url.request(redirect_count + 1)  # 재귀 호출
#         else:
#             raise Exception("Location 헤더 없음")
#
#     # 5. 정상 응답 처리
#     return body

import socket
import ssl
import tkinter
import tkinter.font

class URL:
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"]

        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url

        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    def request(self, redirect_count=0):
        # 리다이렉트 루프 방지를 위한 최대 리다이렉트 횟수 제한
        MAX_REDIRECTS = 10

        # 최대 리다이렉트 횟수 초과 시 예외 발생
        if redirect_count >= MAX_REDIRECTS:
            raise Exception(f"Too many redirects (maximum {MAX_REDIRECTS})")

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
        s.send(request.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")

        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        # 300번대 상태 코드 처리 (리다이렉트)
        if status.startswith("3"):
            # Location 헤더에서 리다이렉트 URL 가져오기
            print(f"Redirected {status} to {response_headers.get('location', '')}")
            if "location" in response_headers:
                location = response_headers["location"]
                s.close()

                # Location이 전체 URL인 경우 (스킴과 호스트 포함)
                if location.startswith("http://") or location.startswith("https://"):
                    # 새로운 URL 객체 생성하여 재귀적으로 요청
                    new_url = URL(location)
                    return new_url.request(redirect_count + 1)
                else:
                    # 상대 경로인 경우 (같은 호스트와 스킴 사용)
                    # 경로가 /로 시작하지 않으면 /를 추가
                    if not location.startswith("/"):
                        location = "/" + location

                    # 현재 URL의 스킴과 호스트를 사용하여 새 URL 생성
                    new_url_string = f"{self.scheme}://{self.host}"
                    if (self.scheme == "http" and self.port != 80) or \
                       (self.scheme == "https" and self.port != 443):
                        new_url_string += f":{self.port}"
                    new_url_string += location

                    new_url = URL(new_url_string)
                    return new_url.request(redirect_count + 1)
            else:
                # Location 헤더가 없는 경우 예외 발생
                raise Exception(f"Redirect response (status {status}) without Location header")

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        body = response.read()
        s.close()

        return body

class Text:
    def __init__(self, text):
        self.text = text

class Tag:
    def __init__(self, tag):
        self.tag = tag

def lex(body):
    out = []
    buffer = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
            if buffer: out.append(Text(buffer))
            buffer = ""
        elif c == ">":
            in_tag = False
            out.append(Tag(buffer))
            buffer = ""
        else:
            buffer += c
    if not in_tag and buffer:
        out.append(Text(buffer))
    return out

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18

SCROLL_STEP = 100

FONTS = {}

def get_font(size, weight, style):
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight,
            slant=style)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]

class Layout:
    def __init__(self, tokens):
        self.tokens = tokens
        self.display_list = []

        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 12

        self.line = []
        for tok in tokens:
            self.token(tok)
        self.flush()

    def token(self, tok):
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word)
        elif tok.tag == "i":
            self.style = "italic"
        elif tok.tag == "/i":
            self.style = "roman"
        elif tok.tag == "b":
            self.weight = "bold"
        elif tok.tag == "/b":
            self.weight = "normal"
        elif tok.tag == "small":
            self.size -= 2
        elif tok.tag == "/small":
            self.size += 2
        elif tok.tag == "big":
            self.size += 4
        elif tok.tag == "/big":
            self.size -= 4
        elif tok.tag == "br":
            self.flush()
        elif tok.tag == "/p":
            self.flush()
            self.cursor_y += VSTEP

    def word(self, word):
        font = get_font(self.size, self.weight, self.style)
        w = font.measure(word)
        if self.cursor_x + w > WIDTH - HSTEP:
            self.flush()
        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        if not self.line: return
        metrics = [font.metrics() for x, word, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent
        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = HSTEP
        self.line = []

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()
        self.scroll = 0

        self.window.bind("<Down>", self.scrolldown)
        self.display_list = []

    def load(self, url):
        body = url.request()
        tokens = lex(body)
        self.display_list = Layout(tokens).display_list
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, word, font in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + font.metrics("linespace") < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=word, font=font, anchor="nw")

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

if __name__ == "__main__":
    import sys
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
