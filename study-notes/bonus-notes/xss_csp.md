# XSS와 CSP: 최후의 클라이언트 측 방어선

## 1. XSS와 CSRF의 근본적인 차이: 탈취 vs 위조

웹 보안을 이해하기 위해선 XSS와 CSRF의 목표를 명확히 구분하는 것이 중요합니다.

- **CSRF (사이트 간 요청 위조):** 이 공격의 목적은 **'권한 도용'**입니다. 공격자는 사용자의 인증 상태(쿠키)를 이용하여, 피해자의 의도와는 다른 요청(글 삭제, 송금 등)을 서버로 보내도록 **'위조'**합니다. 공격자는 정보를 훔치지 않고, 단지 사용자인 척 행동을 시킬 뿐입니다.

- **XSS (사이트 간 스크립팅):** 이 공격의 주된 목적은 **'정보 탈취'**이며, 궁극적으로는 **'브라우저 제어권 장악'**에 이릅니다. 공격자는 신뢰된 웹사이트에 악성 스크립트를 주입하여, 피해자의 브라우저에서 직접 코드를 실행시킵니다. 이를 통해 세션 쿠키, 개인정보, 키 입력 등 민감한 정보를 훔치고, 더 나아가 사용자의 권한으로 어떤 악성 행위든 수행할 수 있습니다.

| 구분          | **CSRF (사이트 간 요청 위조)**                     | **XSS (사이트 간 스크립팅)**                   |
| :------------ | :------------------------------------------------- | :--------------------------------------------- |
| **본질**      | 사용자의 **의도와 다른 요청**을 보내게 함          | 신뢰된 사이트에서 **악성 스크립트**를 실행시킴 |
| **주요 목표** | **권한 도용 (행동 위조)**                          | **정보 탈취 및 제어권 장악**                   |
| **비유**      | 사기꾼이 **내 도장이 찍힌 위임장**을 위조하여 제출 | 사기꾼이 **내 집에 직접 들어와** 내 행세를 함  |

## 2. XSS 공격의 종류와 위험성

- **저장 XSS (Stored XSS):** 악성 스크립트가 데이터베이스에 저장되어, 해당 데이터를 조회하는 모든 사용자에게 지속적으로 영향을 미칩니다. (예: 게시판, 댓글)
- **반사 XSS (Reflected XSS):** 악성 스크립트가 URL 파라미터 등에 포함되어, 사용자가 해당 링크를 클릭했을 때만 일회성으로 실행됩니다. (예: 검색 결과 페이지)
- **DOM 기반 XSS (DOM-based XSS):** 이 공격은 서버와 무관하게 브라우저 내에서 발생하여 특히 위험합니다. 악성 페이로드가 서버로 전송되지 않아 **서버 로그에 흔적이 남지 않으며**, 전통적인 서버 측 이스케이프 방어 로직을 우회할 수 있습니다. 예를 들어, `location.hash` 값을 검증 없이 `innerHTML`로 삽입하는 경우 발생할 수 있습니다.

## 3. 전통적인 XSS 방어의 한계

전통적인 XSS 방어는 서버 측에서 이루어지는 **입력값 검증(Input Validation)**과 **출력값 이스케이프(Output Escaping)**에 의존합니다. 이 방법들은 매우 효과적이지만, **개발자의 완벽한 구현에 의존**한다는 치명적인 한계를 가집니다. 복잡한 애플리케이션에서 단 한 곳이라도 처리를 놓치면, 그 즉시 XSS 공격 경로가 열리게 됩니다.

## 4. CSP (Content Security Policy)의 등장: 브라우저에게 규칙을 알려주다

CSP는 전통적인 방어 방식의 한계를 보완하기 위해 등장한, 강력한 브라우저 레벨의 보안 계층입니다.

**CSP란, 서버가 HTTP 응답 헤더를 통해 브라우저에게 "이 웹사이트에서는 오직 내가 허용한 출처(Source)의 리소스(스크립트, 이미지 등)만 로드하고 실행해야 해!"라고 명시적으로 알려주는 보안 정책**입니다. 만약 공격자가 스크립트 주입에 성공하더라도, 브라우저는 CSP 정책을 보고 허용된 출처가 아니므로 실행을 스스로 차단합니다. 즉, 서버 측 방어가 뚫렸을 경우를 대비한 **최후의 방어선(Last Line of Defense)** 역할을 수행합니다.

## 5. CSP의 핵심 지시어와 실제 예시

CSP는 `Content-Security-Policy`라는 HTTP 헤더에 다양한 지시어(Directive)를 설정하여 작동합니다.

- **주요 지시어:** `default-src`, `script-src`, `style-src`, `img-src`, `connect-src`, `frame-ancestors` 등
- **실제 헤더 예시:**
  ```http
  Content-Security-Policy:
    default-src 'self';
    script-src 'self' https://cdn.google.com https://apis.google.com;
    style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
    img-src 'self' data: https:;
    connect-src 'self' https://api.example.com;
    frame-ancestors 'none';
    report-uri /csp-violation-report-endpoint;
  ```

## 6. CSP 구현 전략 및 모범 사례

CSP는 강력하지만 잘못 설정하면 사이트 기능이 마비될 수 있어, 점진적으로 도입하는 것이 중요합니다.

### 리포트 전용 모드로 시작 (Report-Only Mode)

`Content-Security-Policy-Report-Only` 헤더를 사용하면, 브라우저는 정책을 위반하는 리소스를 **차단하지 않고, `report-uri`에 지정된 URL로 위반 보고서만 전송**합니다. 이를 통해 실제 운영에 영향을 주지 않으면서 필요한 CSP 규칙을 완성해나갈 수 있습니다.

- **위반 보고서 예시 (JSON):**
  ```json
  {
    "csp-report": {
      "document-uri": "https://example.com/page",
      "referrer": "",
      "violated-directive": "script-src-elem",
      "effective-directive": "script-src-elem",
      "original-policy": "script-src 'self'; report-uri /csp-violation-report-endpoint",
      "blocked-uri": "https://evil.com/malicious.js",
      "status-code": 200
    }
  }
  ```

### 예외적 인라인 스크립트 허용: Nonce 사용

가장 강력한 CSP는 인라인 스크립트를 금지하는 것이지만, 부득이하게 사용해야 할 경우 `nonce`를 통해 특정 스크립트만 안전하게 허용할 수 있습니다.

- **서버 응답 헤더:**
  ```http
  Content-Security-Policy: script-src 'nonce-aBcDeFg12345'
  ```
- **HTML 본문:**
  ```html
  <script nonce="aBcDeFg12345">
    // 이 스크립트는 헤더의 nonce 값과 일치하므로 실행이 허용됩니다.
    console.log("This is an allowed inline script.");
  </script>
  ```

### 서드파티 라이브러리 관리: SRI (Subresource Integrity)

`script-src`에 서드파티 도메인을 추가할 때는, **SRI**를 함께 사용하여 해당 파일이 중간에 변조되지 않았음을 보장하는 것이 좋습니다.

```html
<script
  src="https://cdn.example.com/library.js"
  integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/ux..."
  crossorigin="anonymous"></script>
```

브라우저는 다운로드한 파일의 해시 값을 계산하여 `integrity` 속성의 값과 비교하고, 일치하지 않으면 스크립트를 실행하지 않습니다.

### Strict CSP: Google이 권장하는 모범 사례

Google은 Nonce 기반 정책에 `'strict-dynamic'` 키워드를 추가하는 "Strict CSP"를 권장합니다. 이를 사용하면 신뢰된 스크립트가 동적으로 생성한 스크립트도 허용되어, 현대적인 자바스크립트 프레임워크 환경에서도 CSP 적용이 용이해집니다.

```http
Content-Security-Policy: script-src 'nonce-{random}' 'strict-dynamic'
```

이 방식은 화이트리스트 관리의 복잡성을 줄이면서도 강력한 보안을 유지할 수 있어, 대규모 애플리케이션에서 특히 유용합니다.

## 7. CSP의 한계: 만능은 아니다

CSP는 강력한 방어선이지만, 모든 것을 해결해주지는 않습니다.

| CSP로 방어 가능                      | CSP로 방어 **불가능**                |
| :----------------------------------- | :----------------------------------- |
| **인라인 및 외부 스크립트 기반 XSS** | CSRF 공격                            |
| 클릭재킹 (`frame-ancestors`)         | 서버 측 취약점 (SQL Injection 등)    |
| 리소스 출처 제한 (이미지, 폰트 등)   | 비즈니스 로직 오류 및 인증/인가 문제 |

- **브라우저 지원:** 구형 브라우저는 CSP를 지원하지 않으므로, 서버 측 방어는 여전히 필수입니다.
- **정책의 허점:** 만약 `script-src`에 `'unsafe-eval'`이나 `'unsafe-inline'`을 허용하면 CSP의 효과가 크게 감소합니다.
- **신뢰된 도메인의 오염:** 허용한 CDN이나 서드파티 도메인이 해킹당하면, 악성 스크립트가 신뢰된 출처를 통해 유입될 수 있습니다. (SRI가 이를 일부 보완)

## 8. 결론: 프론트엔드 개발자를 위한 다층 방어 전략

- **XSS**는 신뢰된 웹사이트에 악성 스크립트를 주입하여 **정보를 탈취하고 브라우저 제어권을 장악**하는 **공격**입니다.
- **입력값 검증 및 출력값 이스케이프**는 XSS를 막기 위한 **서버 측의 1차 방어선**입니다.
- **CSP**는 혹시 모를 1차 방어선의 실패를 대비하여, 브라우저가 스스로 악성 스크립트의 실행을 차단하도록 만드는 **클라이언트 측의 2차 방어선이자 최후의 안전망**입니다.

궁극적으로 안전한 웹을 구축하기 위해서는 CSP와 더불어 `X-Content-Type-Options`, `X-Frame-Options` (또는 CSP의 `frame-ancestors`) 등 다른 보안 헤더를 함께 사용하여 견고한 다층 방어(Defense in Depth) 전략을 수립해야 합니다.
