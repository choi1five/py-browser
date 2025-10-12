# 실행 명령어: python problem/01/06.py https://example.com

# Keep-Alive 구현 (의사코드)

# socket_pool = {}  // 호스트별 소켓 저장

# 요청 함수
    # socket = socket_pool.get(host)  // 풀에서 소켓 찾기
    
    # if socket == null:  // 소켓이 없으면
        # socket.connect(host)  // 3-way handshake
        # socket_pool.add(host, socket)  // 풀에 저장
    
    # try:
        # socket.send(request)  // 요청 전송
        # response = socket.recv()  // 응답 수신
        # return response  // 소켓은 닫지 않음!
        
    # except ConnectionError:  // send 실패 (상대방이 이미 닫음)
        # socket_pool.remove(host)  // 풀에서 제거
        # socket.connect(host)  // 재연결 (3-way handshake)
        # socket_pool.add(host, socket)  // 풀에 다시 저장
        # socket.send(request)  // 재시도
        # response = socket.recv()  // 응답 수신
        # return response


# 백그라운드 타임아웃 관리
    # while true:  // 무한 반복
        # sleep(1)  // 1초마다 체크
        
        # for socket in socket_pool:  // 모든 소켓 순회
            # if timeout(socket, 5):  // 5초 이상 사용 안 함
                # socket.close()  // 연결 종료 (4-way handshake)
                # socket_pool.remove(socket)  // 풀에서 제거

import socket
import ssl


# 소켓 풀 - keep-alive 연결들을 관리하는 전역 딕셔너리
socket_pool = {}


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

    def get_pooled_connection(self):
        """소켓 풀에서 keep-alive 연결을 가져오거나 새 연결 생성"""
        # 연결 키: (host, port, scheme)
        connection_key = (self.host, self.port, self.scheme)

        # 소켓 풀에서 기존 연결 확인 (이전에 keep-alive로 저장된 연결만)
        if connection_key in socket_pool:
            pooled_socket = socket_pool[connection_key]

            if self.is_socket_alive(pooled_socket, connection_key):
                print(f"=== 소켓 풀에서 keep-alive 연결 재사용: {self.host}:{self.port} ===")
                return pooled_socket

        # 새로운 연결 생성
        print(f"=== 새로운 연결 생성: {self.host}:{self.port} ===")
        return self.create_new_connection()

    def is_socket_alive(self, sock, connection_key):
        """소켓이 살아있고 사용 가능한지 확인"""
        try:
            # 소켓이 닫혔는지 확인
            if sock.fileno() == -1:
                print(f"=== 소켓이 이미 닫힘: {connection_key} ===")
                self.remove_from_pool(connection_key)
                return False

            # SSL 소켓과 일반 소켓에 따라 다른 방식으로 연결 상태 확인
            if isinstance(sock, ssl.SSLSocket):
                # SSL 소켓의 경우 pending() 메서드로 읽을 데이터가 있는지 확인
                # 연결이 살아있다면 0을 반환하고, 끊어졌다면 예외 발생
                try:
                    sock.pending()
                    print(f"=== SSL 소켓 연결 상태 양호: {connection_key} ===")
                    return True
                except ssl.SSLError:
                    print(f"=== SSL 소켓 연결 끊어짐: {connection_key} ===")
                    self.remove_from_pool(connection_key)
                    return False
            else:
                # 일반 소켓의 경우 MSG_PEEK으로 연결 상태 확인
                old_timeout = sock.gettimeout()
                sock.settimeout(0.1)
                try:
                    data = sock.recv(1, socket.MSG_PEEK)
                    if len(data) == 0:
                        # 연결이 정상적으로 종료됨 (FIN 받음)
                        print(f"=== 소켓이 서버에 의해 종료됨: {connection_key} ===")
                        self.remove_from_pool(connection_key)
                        return False
                    print(f"=== 소켓 연결 상태 양호: {connection_key} ===")
                    return True
                except socket.timeout:
                    # 타임아웃은 정상 - 읽을 데이터가 없다는 뜻
                    print(f"=== 소켓 연결 상태 양호 (타임아웃): {connection_key} ===")
                    return True
                except (socket.error, OSError):
                    print(f"=== 소켓 연결 오류: {connection_key} ===")
                    self.remove_from_pool(connection_key)
                    return False
                finally:
                    sock.settimeout(old_timeout)

        except Exception as e:
            print(f"=== 소켓 상태 확인 중 오류: {connection_key}, {e} ===")
            self.remove_from_pool(connection_key)
            return False

    def remove_from_pool(self, connection_key):
        """소켓 풀에서 연결 제거"""
        if connection_key in socket_pool:
            try:
                socket_pool[connection_key].close()
            except:
                pass
            del socket_pool[connection_key]
            print(f"=== 소켓 풀에서 제거됨: {connection_key} ===")

    def create_new_connection(self):
        """새로운 소켓 연결 생성 (캐시에 저장하지 않음)"""
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )

        s.connect((self.host, self.port))

        # HTTPS의 경우 SSL 래핑
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        return s

    def request(self, close_connection=False):
        # 소켓 풀에서 연결을 가져오거나 새 연결 생성
        s = self.get_pooled_connection()

        try:
            # HTTP 요청 생성 (HTTP/1.1은 기본적으로 keep-alive)
            request = "GET {} HTTP/1.1\r\n".format(self.path)  # HTTP/1.1 사용 (1-1 문제에서 변경)
            request += "Host: {}\r\n".format(self.host)

            # Connection 헤더는 close할 때만 명시 (HTTP/1.1 기본값 활용)
            if close_connection:
                request += "Connection: close\r\n"  # 연결 종료 요청
                print(f"=== 클라이언트가 Connection: close 명시 요청 ===")
            else:
                # HTTP/1.1에서는 Connection 헤더를 생략하면 기본적으로 keep-alive
                print(f"=== HTTP/1.1 기본 keep-alive 사용 (Connection 헤더 생략) ===")

            request += "User-Agent: PythonBrowser/1.0\r\n"
            request += "\r\n"

            # 요청 내용 확인을 위해 출력
            print("=== 전송하는 HTTP 요청 ===")
            print(repr(request))
            print("=== 요청 내용 (개행 적용) ===")
            print(request.replace('\r\n', '\n'), end="")
            print("======================")

            s.send(request.encode("utf-8"))

            # 응답 헤더 읽기
            response = s.makefile("r", encoding="utf-8", newline="\r\n")
            statusline = response.readline()
            version, status, explanation = statusline.split(" ", 2)

            response_headers = {}
            while True:
                line = response.readline()
                if line == "\r\n":
                    break
                header, value = line.split(":", 1)
                response_headers[header.lower()] = value.strip()

            print("=== 응답 헤더 ===")
            print(f"Status: {statusline.strip()}")
            for header, value in response_headers.items():
                print(f"{header}: {value}")
            print("================")

            assert "transfer-encoding" not in response_headers
            assert "content-encoding" not in response_headers

            # Content-Length 기반으로 바디를 정확히 읽기 (Connection: close 대신)
            content_length = int(response_headers.get("content-length", 0))
            print(f"=== Content-Length: {content_length} bytes ===")

            if content_length > 0:
                # Content-Length만큼만 정확히 읽기
                body = response.read(content_length)
            else:
                # Content-Length가 없으면 기존 방식으로 읽기
                body = response.read()

            # 서버 응답에 따른 연결 관리 (핵심 keep-alive 로직!)
            connection_key = (self.host, self.port, self.scheme)
            connection_header = response_headers.get("connection", "").lower()

            # 클라이언트가 close를 요청했으면 무조건 연결 종료
            if close_connection:
                print("=== 클라이언트가 close 요청했으므로 연결 종료 ===")
                s.close()
                if connection_key in socket_pool:
                    del socket_pool[connection_key]
            elif connection_header == "keep-alive":
                print("=== 서버가 keep-alive 응답, 소켓 풀에 저장 ===")
                # 서버가 keep-alive로 응답했을 때만 소켓 풀에 저장
                socket_pool[connection_key] = s
            elif connection_header == "close":
                print("=== 서버가 Connection: close 응답, 연결 종료 ===")
                s.close()
                # 소켓 풀에서 제거 (혹시 있다면)
                if connection_key in socket_pool:
                    del socket_pool[connection_key]
            else:
                # HTTP/1.1에서 Connection 헤더가 없으면 기본적으로 keep-alive
                print("=== Connection 헤더 없음, HTTP/1.1 기본 keep-alive로 소켓 풀에 저장 ===")
                socket_pool[connection_key] = s

            # response 파일 객체는 닫지만 소켓은 keep-alive인 경우 유지
            response.close()

            return body

        except (socket.error, ssl.SSLError, OSError) as e:
            # 연결 오류 발생 시 소켓 풀에서 제거하고 재시도
            print(f"=== 연결 오류 발생: {e} ===")
            connection_key = (self.host, self.port, self.scheme)
            self.remove_from_pool(connection_key)
            try:
                s.close()
            except:
                pass

            # 재귀적으로 다시 시도 (새로운 연결로)
            print("=== 새로운 연결로 재시도 ===")
            return self.request()


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


def test_connection_reuse():
    """연결 재사용 테스트 함수"""
    print("=== 연결 재사용 테스트 시작 ===")

    # 같은 서버로 여러 번 요청하여 연결 재사용 확인
    url1 = URL("https://httpbin.org/get")
    url2 = URL("https://httpbin.org/headers")
    url3 = URL("https://httpbin.org/user-agent")

    print("\n1️⃣ 첫 번째 요청 (keep-alive):")
    body1 = url1.request(close_connection=False)  # keep-alive 요청
    print(f"응답 길이: {len(body1)} bytes")

    print("\n2️⃣ 두 번째 요청 (keep-alive, 재사용 기대):")
    body2 = url2.request(close_connection=False)  # keep-alive 요청
    print(f"응답 길이: {len(body2)} bytes")

    print("\n3️⃣ 세 번째 요청 (close로 연결 종료):")
    body3 = url3.request(close_connection=True)  # close 요청
    print(f"응답 길이: {len(body3)} bytes")

    print(f"\n현재 소켓 풀의 연결 수: {len(socket_pool)}")

    # 같은 서버에 다시 요청 (새 연결이 생성되어야 함)
    print("\n4️⃣ 네 번째 요청 (같은 서버, 하지만 이전에 close 했으므로 새 연결):")
    url4 = URL("https://httpbin.org/json")
    body4 = url4.request(close_connection=False)  # keep-alive 요청
    print(f"응답 길이: {len(body4)} bytes")

    # 다른 서버로 요청하여 새로운 연결이 생성되는지 확인
    print("\n5️⃣ 다섯 번째 요청 (다른 서버):")
    url5 = URL("https://example.com")
    body5 = url5.request(close_connection=False)  # keep-alive 요청
    print(f"응답 길이: {len(body5)} bytes")

    print(f"\n최종 소켓 풀의 연결 수: {len(socket_pool)}")
    print("소켓 풀 상태:", list(socket_pool.keys()))
    print("=== 연결 재사용 테스트 완료 ===")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        load(URL(sys.argv[1]))
    else:
        # 인자가 없으면 연결 재사용 테스트 실행
        test_connection_reuse()