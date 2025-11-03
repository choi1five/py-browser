# CSS 값 처리의 4단계 (W3C 스펙 기준)

W3C CSS2 스펙에 따르면, **모든 CSS 속성의 최종 값은 4단계의 계산을 거쳐 결정됩니다.** 이 단계들을 이해하는 것은 브라우저가 CSS를 어떻게 해석하고 렌더링하는지 파악하는 데 필수적입니다.

## 4단계 프로세스 흐름

CSS 값은 다음 4가지 단계를 순차적으로 거치며 계산되고 확정됩니다.

```
1. Specified Value (명시된 값)
   ↓
2. Computed Value (계산된 값)
   ↓
3. Used Value (사용된 값)
   ↓
4. Actual Value (실제 값)
```

---

## 1단계: Specified Value (명시된 값)

**정의**: Cascade(우선순위 규칙)를 거쳐 해당 요소의 속성에 대해 최종적으로 결정된 값입니다. 여러 CSS 규칙이 충돌할 때 어떤 값이 선택될지가 이 단계에서 확정됩니다.

### 우선순위 결정 규칙 (The Cascade)

Specified Value는 다음 규칙에 따라 결정됩니다:

1. **해당 요소에 적용되는 선언(Declared Value)이 있으면 사용합니다.**

   - 여러 선언이 충돌할 경우, `!important` 규칙, 출처(Origin), 선택자 특수성(Specificity), 선언 순서(Order)에 따라 우선순위가 결정됩니다.

2. **상속되는 속성이고 부모가 있으면 부모의 Computed Value를 상속받습니다.**

   - `inherit` 키워드를 명시적으로 사용할 수도 있습니다.

3. **위 두 가지 방법으로도 값이 결정되지 않으면, 해당 속성의 초기값(initial value)이 사용됩니다.**
   - `initial` 키워드를 명시적으로 사용할 수도 있습니다.

```html
<style>
  .box {
    color: red; /* ← 선언된 값 중 캐스케이딩을 통해 최종 선택 */
    width: 50%; /* ← 선언된 값 중 캐스케이딩을 통해 최종 선택 */
    font-size: 2em; /* ← 선언된 값 중 캐스케이딩을 통해 최종 선택 */
  }
</style>
```

---

## 2단계: Computed Value (계산된 값)

**정의**: Specified Value를 기반으로, **문서의 레이아웃(렌더링) 정보 없이도 확정될 수 있는 모든 상대적인 단위를 절대 값으로 변환한 값**입니다. 이 단계의 값은 상속 시 자식에게 전달됩니다.

### 주요 특징

- **레이아웃 독립적 계산:** 요소를 렌더링하거나 레이아웃 정보를 분석하지 않고도 계산이 가능합니다.
- **단위 변환:**
  - `em`, `ex`, `rem`, `vw`, `vh` 등 상대적인 길이 단위는 절대적인 픽셀(px) 값으로 변환됩니다.
  - URI (Uniform Resource Identifier)는 절대 경로로 변환됩니다.
  - 키워드 값 (`red`, `bold` 등)은 표준화된 절대 값 (`rgb(255, 0, 0)`, `700` 등)으로 변환됩니다.
- **퍼센트 유지:** `width: 50%`와 같이 부모 요소의 크기에 의존하는 퍼센트 값은 이 단계에서 아직 부모의 정확한 크기를 알 수 없으므로 그대로 퍼센트로 유지됩니다.
- **auto 유지:** `width: auto`와 같은 값도 이 단계에서는 그대로 유지됩니다.

```css
/* Specified Value → Computed Value 예시 */

font-size: 2em;
→ Computed: 32px        /* (기준 font-size가 16px일 때) em을 픽셀로 계산 */

color: red;
→ Computed: rgb(255, 0, 0)  /* 키워드를 RGB로 변환 */

font-weight: bold;
→ Computed: 700         /* 키워드를 숫자로 변환 */

width: 50%;
→ Computed: 50%         /* 부모 크기를 알 수 없으므로 퍼센트 유지 */

width: auto;
→ Computed: auto        /* 아직 구체적 값 아님 */

background: url(image.png);
→ Computed: url(https://example.com/image.png)  /* 상대 경로를 절대 경로로 */
```

### 상속과의 관계 (매우 중요)

상속이 발생하는 경우, 자식 요소는 부모 요소의 **Computed Value**를 상속받습니다. 부모의 Computed Value가 자식의 Specified Value이자 Computed Value가 됩니다.

```html
<style>
  body {
    font-size: 10pt;
  } /* body의 Computed font-size = 10pt */
  h1 {
    font-size: 130%;
  }
</style>

<body>
  <h1>A <em>large</em> heading</h1>
</body>
```

`h1`의 `font-size` Specified Value는 `130%`입니다. 이는 부모인 `body`의 `font-size` Computed Value인 `10pt`에 상대적이므로, `h1`의 `font-size` Computed Value는 13pt (130% × 10pt)가 됩니다.
그리고 `em` 요소는 `h1`의 자식이므로, `h1`의 Computed Value인 `13pt`를 상속받아 `em`의 Computed `font-size`도 `13pt`가 됩니다.

### inherit 키워드 처리

```css
.parent {
  border: 2px solid red;
}

.child {
  border: inherit; /* inherit 키워드 사용 */
}

/* .child의 border 처리:
   Specified: inherit
   Computed: 2px solid rgb(255, 0, 0)  (부모의 Computed Value 상속)
*/
```

---

## 3단계: Used Value (사용된 값)

**정의**: Computed Value를 기반으로, **실제 문서의 레이아웃이 계산된 후에야 비로소 확정될 수 있는 모든 상대적인 값(예: % 너비/높이, auto)을 절대적인 값으로 변환한 결과**입니다. 이 값은 요소의 박스 모델을 구성하는 데 사용됩니다.

### 언제 계산되나?

일부 값(예: `width`, `height`, `margin`, `padding`의 퍼센트 값)은 요소가 포함된 블록(Containing Block)의 크기를 알아야 최종적인 절대 값으로 변환될 수 있습니다. 이러한 값들은 문서의 레이아웃이 결정될 때 비로소 확정됩니다.

```html
<div class="parent" style="width: 1000px;">
  <div class="child" style="width: 50%;"></div>
</div>
```

```
.child의 width:
- Specified Value: 50%
- Computed Value: 50%         (부모 크기를 아직 모름)
- Used Value: 500px           (레이아웃 계산 후, 부모의 1000px에 50% 적용)
```

Used Value는 원칙적으로 브라우저가 요소를 화면에 배치하고 박스 모델을 구성하는 데 사용하는 값입니다. 이 단계에서 모든 상대적인 단위는 최종적인 절대 픽셀 값 등으로 변환됩니다.

```css
/* Used Value 예시: 모든 상대 단위가 절대 값으로 변환됨 */

width: 50%;
→ Used: 500px           /* 부모가 1000px일 때 */

margin: 10%;
→ Used: 100px           /* 부모 width가 1000px일 때의 10% */

width: auto;
→ Used: 800px           /* 콘텐츠/컨테이너 기반 계산 */

height: auto;
→ Used: 237px           /* 콘텐츠 높이 계산 후 결정된 실제 높이 */
```

---

## 4단계: Actual Value (실제 값)

**정의**: Used Value를 기반으로, **사용자 에이전트(User Agent, 브라우저)의 실제 렌더링 환경(예: 화면 해상도, 픽셀 정렬 방식, 사용 가능한 폰트 등)의 제약 조건에 맞춰 최종적으로 조정된 값**입니다. 이 값이 실제로 화면에 그려집니다.

### 왜 필요한가?

Used Value가 계산된 후에도, 브라우저가 해당 환경에서 정확히 그 값을 사용하지 못할 수 있습니다. 이는 다음과 같은 제약 때문일 수 있습니다:

- **서브픽셀 렌더링 불가:** 브라우저가 소수점 이하 픽셀 값을 렌더링하지 못하는 경우 (예: `500.7px` → `501px`로 반올림 또는 내림).
- **디스플레이 환경 제약:** 흑백 디스플레이에서 풀 컬러를 표현할 수 없는 경우, 가장 가까운 흑백 음영으로 조정됩니다.
- **리소스 제약:** 요청된 폰트 크기나 종류가 시스템에 없는 경우, 가장 유사하거나 사용 가능한 폰트로 대체됩니다.

### Used vs Actual 차이

동일한 요소에서 두 단계의 차이를 명확히 보여주는 예시:

```
width:
- Used Value: 500.7px      (계산된 정확한 값)
- Actual Value: 501px      (렌더링 제약으로 반올림)

font-size:
- Used Value: 13pt         (계산된 값)
- Actual Value: 12pt       (13pt 폰트 없음 → 대체)

color:
- Used Value: rgb(123, 234, 45)
- Actual Value: rgb(0, 0, 0)  (흑백 디스플레이 환경)

→ Used는 "계산상 정확한 값"
→ Actual은 "실제 렌더링 가능한 값"
```

예를 들어, H1과 EM의 Computed 및 Used `font-size`가 `13pt`였지만, 브라우저에 `13pt` 폰트가 없다면, 둘 다의 Actual Value는 `12pt`가 될 수 있습니다.

---

## 단계별 비교표

### 기본 비교

| 단계          | 정의                                          | 렌더링 필요 | 상대 단위 처리                     | 예시                                  |
| :------------ | :-------------------------------------------- | :---------- | :--------------------------------- | :------------------------------------ |
| **Specified** | 캐스케이딩을 통해 최종 선택된 값              | ❌          | 그대로 (선언된 형태)               | `50%`, `2em`, `red`, `auto`           |
| **Computed**  | 레이아웃 없이 가능한 만큼 계산 (상속 시 사용) | ❌          | `em`/`rem` → `px`, `%`/`auto` 유지 | `32px`, `50%`, `rgb(255,0,0)`, `auto` |
| **Used**      | 레이아웃 계산 완료 후 모든 의존성 해결        | ✅          | 모두 절대값으로 변환 (`px` 등)     | `500px`, `32px`, `800px`              |
| **Actual**    | 환경 제약 반영 후 최종 값                     | ✅          | 모두 절대값 (`px` 등)              | `501px` (반올림), `12pt` (대체)       |

### 상세 단위별 처리

| 단계          | em/rem      | %           | auto        | 키워드          |
| ------------- | ----------- | ----------- | ----------- | --------------- |
| **Specified** | 그대로      | 그대로      | 그대로      | 그대로          |
| **Computed**  | → px        | 유지        | 유지        | → 절대값        |
| **Used**      | → px        | → px        | → px        | → 절대값        |
| **Actual**    | → px (조정) | → px (조정) | → px (조정) | → 절대값 (조정) |

---

## getComputedStyle()과의 관계

JavaScript의 `window.getComputedStyle()` 메서드는 요소의 최종 계산된 스타일을 가져오지만, 반환하는 값은 속성에 따라 Used Value 또는 Computed Value가 될 수 있습니다.

```javascript
const element = document.querySelector(".box");
const styles = getComputedStyle(element);

// 규칙: 레이아웃 의존적 속성 → Used Value 반환
console.log(styles.width); // "500px" (Used Value)
console.log(styles.height); // "300px" (Used Value)
console.log(styles.top); // "100px" (Used Value)
console.log(styles.marginLeft); // "20px" (Used Value)

// 규칙: 레이아웃 독립적 속성 → Computed Value 반환
console.log(styles.color); // "rgb(255, 0, 0)" (Computed Value)
console.log(styles.fontSize); // "32px" (Computed Value)
console.log(styles.lineHeight); // "normal" (Computed Value)
console.log(styles.fontFamily); // "Arial, sans-serif" (Computed Value)
```

일반적으로 `getComputedStyle()`은 레이아웃에 직접적인 영향을 주는 `width`, `height`, `top`, `left` 등은 Used Value를 반환하고, 그 외의 대부분 속성(색상, 폰트 등)은 Computed Value를 반환합니다.

---

## 실전 예시: 전체 프로세스

```html
<style>
  body {
    font-size: 16px; /* Computed: 16px */
  }

  .container {
    width: 1000px; /* Computed: 1000px */
  }

  .box {
    width: 50%; /* Specified */
    font-size: 1.5em; /* Specified */
    padding: 2%; /* Specified */
    line-height: normal; /* Specified */
  }
</style>

<div class="container">
  <div class="box">텍스트 내용</div>
</div>
```

### `.box` 요소의 각 속성별 값 처리

**`width` 속성:**

```
1. Specified: 50%
2. Computed: 50%              (부모 .container의 크기를 아직 알 수 없음)
3. Used: 500px                (.container의 width 1000px에 50% 적용)
4. Actual: 500px              (500px는 정수이므로 그대로 렌더링 가능)
```

**`font-size` 속성:**

```
1. Specified: 1.5em
2. Computed: 24px             (부모 body의 font-size 16px × 1.5)
3. Used: 24px                 (동일한 값, 레이아웃에 직접 영향 없음)
4. Actual: 24px               (24px 폰트 사용 가능하다고 가정)
```

**`padding` 속성:**

```
1. Specified: 2%
2. Computed: 2%               (부모 .container의 width를 아직 알 수 없음)
3. Used: 20px                 (.container의 width 1000px에 2% 적용)
4. Actual: 20px               (20px는 정수이므로 그대로 렌더링 가능)
```

**`line-height` 속성:**

```
1. Specified: normal
2. Computed: normal           (아직 구체적인 절대 값 없음, 브라우저 기본값)
3. Used: 28.8px               (Computed font-size 24px에 브라우저 기본 factor 적용)
4. Actual: 29px               (브라우저가 서브픽셀 렌더링 불가 시 반올림)
```

---

## 핵심 정리

### Computed Value의 역할

- 문서 렌더링 없이 계산 가능한 값
- `em`, `rem`, `vw`, `vh` 등 상대 단위는 절대값으로, `%`와 `auto`는 유지
- **상속될 때 자식 요소에게 전달되는 값**
- 성능 최적화: 상속 시 재계산 불필요

### Used Value의 역할

- 레이아웃 계산 완료 후, 모든 의존성을 해결하여 얻은 절대값
- 실제로 요소의 박스 모델을 구성하고 렌더링에 사용되는 값
- `%`, `auto` 등이 모두 픽셀 등 절대값으로 변환됨

### Actual Value의 역할

- 브라우저의 렌더링 환경 제약을 반영하여 최종적으로 조정된 값
- 실제 화면에 그려지는 최종적인 값
- 서브픽셀 처리, 폰트 대체, 색상 제한 등 반영

---

## 결론

**W3C 스펙에 따르면 CSS 값 처리는 명확히 4단계로 구분되며, 각 단계는 고유한 목적과 역할을 가집니다:**

✅ **Specified** → 우선순위 충돌 해결

- CSS 규칙 결정 (`!important`, 출처, 특수성, 선언 순서에 따라)

✅ **Computed** → 상속 최적화

- 가능한 만큼 계산 (한 번만 계산하여 상속에 사용)
- 상속 시 재계산 불필요

✅ **Used** → 레이아웃 반영

- 레이아웃 후 절대값 (렌더링에 사용)
- 모든 의존성 해결

✅ **Actual** → 환경 적응

- 환경 제약 반영 (최종 화면에 그려지는 값)
- 다양한 환경 대응

**이 4단계 분리를 통해 브라우저는:**

- 효율적으로 상속 처리 (Computed Value 재사용)
- 레이아웃 계산 최적화 (필요한 시점에만 계산)
- 다양한 환경에 적응 (Actual Value 조정)

이 4단계는 브라우저가 CSS를 처리하고 웹 페이지를 화면에 그리는 정확한 메커니즘을 정의하며, 개발자가 CSS 동작을 깊이 이해하는 데 중요한 기반이 됩니다.
