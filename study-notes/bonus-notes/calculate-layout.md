# Width vs Height 계산 방향 (실전 HTML/CSS 예시)

## 📦 Case 1: Block Mode

### HTML/CSS 코드

```html
<style>
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  p {
    font-size: 16px;
    line-height: 1.25; /* 16px * 1.25 = 20px */
  }
</style>

<div class="container" style="width: 800px; background: #f0f0f0;">
  <p style="background: #ffcccc;">첫 번째 문단입니다.</p>
  <div style="background: #ccffcc;">
    <p style="background: #ffffcc;">중첩된 문단</p>
    <p style="background: #ffffcc;">또 다른 문단</p>
  </div>
  <p style="background: #ccccff;">마지막 문단입니다.</p>
</div>
```

### 브라우저 렌더링 결과

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ container (width: 800px, background: #f0f0f0)        ┃
┃ ┌─────────────────────────────────────────────────┐ ┃
┃ │ <p> 첫 번째 문단입니다. (#ffcccc)                │ ┃ ← height: 20px
┃ │     font-size: 16px × line-height: 1.25 = 20px  │ ┃   (16 × 1.25)
┃ └─────────────────────────────────────────────────┘ ┃
┃ ┌─────────────────────────────────────────────────┐ ┃
┃ │ <div> (#ccffcc)                                 │ ┃
┃ │  ┌───────────────────────────────────────────┐  │ ┃
┃ │  │ <p> 중첩된 문단 (#ffffcc)                 │  │ ┃ ← height: 20px
┃ │  └───────────────────────────────────────────┘  │ ┃   (16 × 1.25)
┃ │  ┌───────────────────────────────────────────┐  │ ┃
┃ │  │ <p> 또 다른 문단 (#ffffcc)                │  │ ┃ ← height: 20px
┃ │  └───────────────────────────────────────────┘  │ ┃   (16 × 1.25)
┃ └─────────────────────────────────────────────────┘ ┃ ← height: 40px (20+20)
┃ ┌─────────────────────────────────────────────────┐ ┃
┃ │ <p> 마지막 문단입니다. (#ccccff)                │ ┃ ← height: 20px
┃ └─────────────────────────────────────────────────┘ ┃   (16 × 1.25)
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
  ↑ height: 80px (20+40+20)
```

### 계산 과정 시각화 (깊이 우선 탐색)

```
재귀 실행 순서 (DFS - Depth First Search)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

container.layout() 시작
│
├─ ⬇️ Width 전달 (재귀 이전)
│  container.width = 800
│  자식 생성: [p1, div, p4]
│
├─ 🔄 재귀 호출 (for child in children)
│  │
│  ├─ ① p1.layout() ──────────────────┐
│  │  ├─ p1.width = 800 ⬇️             │ 첫 번째 자식
│  │  ├─ 인라인 텍스트 처리            │
│  │  └─ p1.height = 20 ⬆️ ✓          │
│  │                                   │
│  ├─ ② div.layout() ──────────────────┼─┐
│  │  ├─ div.width = 800 ⬇️            │ │ 두 번째 자식
│  │  ├─ 자식 생성: [p2, p3]          │ │ (자식이 있으니 더 깊이!)
│  │  │                                │ │
│  │  ├─ 🔄 재귀 (div의 자식들)        │ │
│  │  │  │                             │ │
│  │  │  ├─ ③ p2.layout() ─────────────┼─┼─┐
│  │  │  │  ├─ p2.width = 800 ⬇️       │ │ │ div의 첫 번째 자식
│  │  │  │  ├─ 인라인 텍스트 처리      │ │ │
│  │  │  │  └─ p2.height = 20 ⬆️ ✓    │ │ │
│  │  │  │                             │ │ │
│  │  │  └─ ④ p3.layout() ─────────────┼─┼─┤
│  │  │     ├─ p3.width = 800 ⬇️       │ │ │ div의 두 번째 자식
│  │  │     ├─ 인라인 텍스트 처리      │ │ │
│  │  │     └─ p3.height = 20 ⬆️ ✓    │ │ │
│  │  │                                │ │ │
│  │  └─ ⑤ div.height = 40 ⬆️ ✓ ──────┼─┼─┘
│  │     (p2 + p3 = 20 + 20)          │ │ 자식들 완료 후 계산!
│  │                                   │ │
│  └─ ⑥ p4.layout() ──────────────────┼─┘
│     ├─ p4.width = 800 ⬇️             │ 세 번째 자식
│     ├─ 인라인 텍스트 처리            │
│     └─ p4.height = 20 ⬆️ ✓          │
│                                      │
└─ ⑦ container.height = 80 ⬆️ ✓ ─────┘
   (p1 + div + p4 = 20 + 40 + 20)    모든 자식 완료 후 계산!


실행 타임라인
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

t1:  container 시작 (width=800 설정)
     │
t2:  ├─ p1 시작 (width=800)
t3:  └─ p1 완료 (height=20) ✓
     │
t4:  ├─ div 시작 (width=800)
     │   │
t5:  │   ├─ p2 시작 (width=800)
t6:  │   └─ p2 완료 (height=20) ✓
     │   │
t7:  │   ├─ p3 시작 (width=800)
t8:  │   └─ p3 완료 (height=20) ✓
     │   │
t9:  └─ div 완료 (height=40) ✓  ← p2, p3 모두 완료 후!
     │
t10: ├─ p4 시작 (width=800)
t11: └─ p4 완료 (height=20) ✓
     │
t12: container 완료 (height=80) ✓  ← 모든 자식 완료 후!


핵심 포인트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Width: 재귀 이전에 부모→자식으로 즉시 전달 (Top-down)
✓ Height: 재귀 이후에 자식→부모로 집계 (Bottom-up)
✓ 실행 순서: 깊이 우선 탐색 (DFS)
  → p1 완료 → div 시작 → p2 완료 → p3 완료 → div 완료 → p4 완료
✓ 형제로 넘어가기 전에 자식의 모든 하위 트리를 완전히 처리!
```

---

## 📝 Case 2: Inline Mode

### HTML/CSS 코드

```html
<style>
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  p {
    font-size: 16px;
    line-height: 1.25; /* 기본 줄 높이 */
  }
  b {
    font-size: 20px; /* 더 큰 폰트 */
  }
  small {
    font-size: 12px; /* 더 작은 폰트 */
  }
</style>

<p style="width: 400px; background: #f0f0f0;">
  Hello world this is a
  <b>very long</b>
  text that will
  <small>definitely wrap</small>
  to multiple lines here
</p>
```

### 브라우저 렌더링 결과

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ <p> (width: 400px, background: #f0f0f0)       ┃
┃                                                ┃
┃  Line 1: Hello world this is a [very]         ┃ ← height: 25px
┃          ^^^^^^^^^^^^^^^^^^^^  ^^^^^^            (20px * 1.25 = 25px)
┃          16px (기본)            20px (bold)       max_ascent 기준
┃                                                ┃
┃  Line 2: [long] text that will                ┃ ← height: 25px
┃          ^^^^^^ ^^^^^^^^^^^^^^                    (20px * 1.25 = 25px)
┃          20px   16px                           ┃
┃                                                ┃
┃  Line 3: [definitely] to multiple lines       ┃ ← height: 20px
┃          ^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^          (16px * 1.25 = 20px)
┃          12px        16px                      ┃
┃                                                ┃
┃  Line 4: here                                 ┃ ← height: 20px
┃          ^^^^                                     (16px * 1.25 = 20px)
┃          16px                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
  ↑ height: 90px (25+25+20+20)
```

### 계산 과정 시각화

```
Step 1: Width 전달 (⬇️ Top-down)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
p.width = 400
         │
         └─→ 줄바꿈 기준으로 사용


Step 2: 텍스트 배치 (Inline 레이아웃)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cursor_x = 0, cursor_y = 0

word("Hello", 16px)   → cursor_x = 50
word("world", 16px)   → cursor_x = 100
word("this", 16px)    → cursor_x = 140
word("is", 16px)      → cursor_x = 160
word("a", 16px)       → cursor_x = 175
word("very", 20px)    → cursor_x = 235  (bold, 더 큼!)
word("long", 20px)    → cursor_x = 420 > 400!
                      → flush()
                      → max_ascent = 20 (20px 폰트)
                      → cursor_y = 0 + 1.25 × 20 = 25

cursor_x = 0, cursor_y = 25
word("long", 20px)    → cursor_x = 60
word("text", 16px)    → cursor_x = 110
word("that", 16px)    → cursor_x = 160
word("will", 16px)    → cursor_x = 200
word("definitely", 12px) → cursor_x = 450 > 400!
                      → flush()
                      → max_ascent = 20 (20px 폰트)
                      → cursor_y = 25 + 1.25 × 20 = 50

cursor_x = 0, cursor_y = 50
word("definitely", 12px) → cursor_x = 90  (small, 더 작음!)
word("to", 16px)      → cursor_x = 115
word("multiple", 16px) → cursor_x = 200
word("lines", 16px)   → cursor_x = 250
word("here", 16px)    → cursor_x = 420 > 400!
                      → flush()
                      → max_ascent = 16 (16px 폰트)
                      → cursor_y = 50 + 1.25 × 16 = 70

cursor_x = 0, cursor_y = 70
word("here", 16px)    → cursor_x = 45
                      → flush()
                      → max_ascent = 16
                      → cursor_y = 70 + 1.25 × 16 = 90


Step 3: Height 계산 (⬆️ Bottom-up)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
p.height = cursor_y = 90
```

### flush() 메서드와 CSS의 관계

```python
def flush(self):  # Line 1 예시
    # Line 1: "Hello world this is a very"
    # fonts: [16px, 16px, 16px, 16px, 16px, 20px(bold)]

    # CSS의 font-size에서 나온 값들
    metrics = [font.metrics() for x, word, font in self.line]

    # 가장 큰 ascent 찾기
    max_ascent = max([metric["ascent"] for metric in metrics])
    # = 20 (20px 폰트의 ascent)

    # CSS line-height: 1.25 적용
    baseline = self.cursor_y + 1.25 * max_ascent
    # = 0 + 1.25 × 20 = 25

    # ... 단어들 배치 ...

    max_descent = max([metric["descent"] for metric in metrics])

    # 다음 줄 시작 위치 (line-height 적용)
    self.cursor_y = baseline + 1.25 * max_descent
    # ≈ 25
```

---

## 🎯 핵심 정리

### CSS와 높이 계산의 관계

```css
/* Block Mode */
p {
  font-size: 16px;
  line-height: 1.25; /* → height = 16 × 1.25 = 20px */
}

/* Inline Mode - 여러 폰트 크기 혼합 */
p {
  font-size: 16px;
} /* 기본: 20px (16 × 1.25) */
b {
  font-size: 20px;
} /* 큰 글자: 25px (20 × 1.25) */
small {
  font-size: 12px;
} /* 작은 글자: 15px (12 × 1.25) */
/* 각 줄의 높이 = max 폰트 × 1.25 */
```

|               | Block Mode                | Inline Mode                       |
| ------------- | ------------------------- | --------------------------------- |
| **기본 높이** | `font-size × line-height` | 각 줄마다 `max(font-size) × 1.25` |
| **예시**      | 16px × 1.25 = 20px        | 20px × 1.25 = 25px (bold 때문)    |
| **Width**     | 부모 → 자식 (800px)       | 줄바꿈 기준 (400px)               |
| **Height**    | 자식 합산 (20+40+20=80)   | 줄 높이 누적 (25+25+20+20=90)     |
| **재귀 순서** | DFS (깊이 우선 탐색)      | 재귀 없음 (순차 처리)             |

**깊이 우선 탐색의 핵심:** 형제 노드로 넘어가기 전에 자식의 모든 하위 트리를 완전히 처리합니다! 🌳
