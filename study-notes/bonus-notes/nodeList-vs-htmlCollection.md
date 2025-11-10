# NodeList vs HTMLCollection

## 주요 차이점

| 특징                 | NodeList                                      | HTMLCollection                                                       |
| -------------------- | --------------------------------------------- | -------------------------------------------------------------------- |
| **포함 가능한 노드** | 모든 노드 타입<br>(Element, Text, Comment 등) | Element 노드만                                                       |
| **Live/Static**      | 정적 또는 동적<br>(메서드에 따라 다름)        | 항상 동적 (live)                                                     |
| **forEach() 사용**   | ✅ 가능                                       | ❌ 불가능                                                            |
| **대표 반환 메서드** | `querySelectorAll()`<br>`childNodes`          | `getElementsByClassName()`<br>`getElementsByTagName()`<br>`children` |

---

## NodeList 상세

NodeList는 DOM 노드들의 집합을 나타내는 컬렉션으로, **정적(static)** 또는 **동적(live)** 특성을 가질 수 있습니다. 어떤 메서드로 얻었는지에 따라 그 특성이 달라집니다.

### 1. 정적 (Static) NodeList

`querySelectorAll()`로 얻은 NodeList는 **정적**입니다. 할당 시점의 DOM 상태를 스냅샷처럼 저장하며, 이후 DOM이 변경되어도 영향을 받지 않습니다.

```javascript
// 초기 상태: 3개의 .item 요소
const items = document.querySelectorAll(".item");
console.log(items.length); // 3

// 새 요소 추가
const newItem = document.createElement("div");
newItem.className = "item";
document.body.appendChild(newItem);

// NodeList는 변하지 않음 (정적 스냅샷)
console.log(items.length); // 여전히 3
```

**특징:**

- DOM 변경에 영향받지 않음
- 성능상 유리 (실시간 추적 비용 없음)
- 예측 가능한 동작

### 2. 동적 (Live) NodeList

`childNodes`로 얻은 NodeList는 **동적**입니다. DOM이 변경되면 자동으로 업데이트됩니다.

```javascript
// 초기 자식 노드 수
const children = document.body.childNodes;
console.log(children.length); // 5

// 새 요소 추가
const newDiv = document.createElement("div");
document.body.appendChild(newDiv);

// NodeList가 자동 업데이트됨 (동적)
console.log(children.length); // 6
```

**특징:**

- 실시간 DOM 변경 반영
- 항상 최신 상태 유지
- 추가 메모리 및 성능 비용 발생 가능

### 3. NodeList의 특징

**모든 노드 타입 포함**

NodeList는 **Element 노드뿐만 아니라 Text 노드, Comment 노드 등 모든 노드 타입을 포함**할 수 있습니다.

```javascript
// HTML:
// <div id="container">
//   Hello
//   <span>World</span>
//   <!-- 주석 -->
// </div>

const allNodes = document.getElementById("container").childNodes;

allNodes.forEach((node) => {
  console.log(node.nodeType);
  // 3 (Text: "Hello")
  // 1 (Element: <span>)
  // 3 (Text: 공백)
  // 8 (Comment)
});
```

**forEach() 메서드 사용 가능**

NodeList는 `forEach()` 메서드를 기본 제공합니다.

```javascript
const items = document.querySelectorAll(".item");

// forEach() 직접 사용 가능
items.forEach((item, index) => {
  console.log(`Item ${index}:`, item.textContent);
});
```

---

## HTMLCollection 상세

HTMLCollection은 **항상 동적(live)**이며, **Element 노드만** 포함하는 컬렉션입니다.

### 동적 특성

HTMLCollection은 생성 시점과 관계없이 항상 DOM의 현재 상태를 반영합니다.

```javascript
// 초기 상태: 3개의 .item 요소
const items = document.getElementsByClassName("item");
console.log(items.length); // 3

// 새 요소 추가
const newItem = document.createElement("div");
newItem.className = "item";
document.body.appendChild(newItem);

// 자동으로 업데이트됨
console.log(items.length); // 4

// 요소 제거
document.body.removeChild(newItem);
console.log(items.length); // 3 (다시 감소)
```

**특징:**

- 항상 최신 DOM 상태 반영
- Element 노드만 포함 (Text, Comment 노드 제외)
- `getElementsByTagName()`, `getElementsByClassName()`, `children` 등으로 반환

### forEach() 사용 불가

HTMLCollection은 `forEach()` 메서드가 없습니다. 반복 처리를 위해서는 배열로 변환하거나 다른 방법을 사용해야 합니다.

```javascript
const items = document.getElementsByClassName("item");

// ❌ 에러 발생 - forEach는 함수가 아님
// items.forEach(item => console.log(item));

// ✅ 방법 1: Array.from()으로 변환
Array.from(items).forEach((item) => {
  console.log(item);
});

// ✅ 방법 2: Spread 연산자
[...items].forEach((item) => {
  console.log(item);
});

// ✅ 방법 3: for...of 루프
for (const item of items) {
  console.log(item);
}

// ✅ 방법 4: 전통적인 for 루프
for (let i = 0; i < items.length; i++) {
  console.log(items[i]);
}
```

---

## 왜 둘로 나뉘었는가? (역사적 배경)

NodeList와 HTMLCollection이 별도로 존재하는 이유는 웹 표준의 진화 과정에서 비롯되었습니다. 이는 의도적인 설계라기보다는 **역사적 맥락**과 **하위 호환성 유지**의 결과입니다.

### 1. 역사적 배경

**HTMLCollection (1998년, DOM Level 1)**

초기 DOM API에서 **HTML Element만을 다루기 위한** 목적으로 설계되었습니다.

```javascript
// 1998년부터 존재했던 메서드들
document.getElementsByTagName("div"); // HTMLCollection 반환
document.getElementsByClassName("item"); // HTMLCollection 반환
element.children; // HTMLCollection 반환
```

- Element 노드만 포함
- 항상 live(동적) 특성
- HTML 문서 구조를 동적으로 추적하는 것이 주 목적

**NodeList (조금 후, 다른 목적)**

HTML Element뿐만 아니라 **모든 종류의 노드**를 다루기 위해 설계되었습니다.

```javascript
// 모든 자식 노드 (Element + Text + Comment)
element.childNodes; // NodeList 반환 (동적)

// 특정 선택자에 매칭되는 노드들
document.querySelectorAll(".item"); // NodeList 반환 (정적, 2013년 추가)
```

- 모든 노드 타입 포함 가능
- 정적 또는 동적 특성
- DOM 트리 전체 구조를 표현하는 것이 주 목적

### 2. 설계상 의미 차이

**HTMLCollection: "HTML 요소들의 컬렉션"**

```javascript
// HTML 문서의 div 요소만 수집
const divs = document.getElementsByTagName("div");

// 오직 <div> Element만 포함
// Text 노드나 Comment는 포함되지 않음
```

**NodeList: "모든 종류의 노드 리스트"**

```javascript
// <body>의 모든 자식 노드
const nodes = document.body.childNodes;

// Element + Text + Comment 노드 모두 포함
nodes.forEach((node) => {
  switch (node.nodeType) {
    case Node.ELEMENT_NODE: // 1
      console.log("Element:", node.tagName);
      break;
    case Node.TEXT_NODE: // 3
      console.log("Text:", node.textContent);
      break;
    case Node.COMMENT_NODE: // 8
      console.log("Comment:", node.textContent);
      break;
  }
});
```

### 3. querySelector 시리즈의 등장 (2013년경)

`querySelectorAll()`이 새롭게 추가될 때, W3C는 **정적 NodeList**를 반환하도록 결정했습니다.

**결정 이유:**

1. **성능 최적화**

   - Live 업데이트는 지속적인 DOM 감시 비용 발생
   - 정적 스냅샷은 한 번만 수집하면 됨

2. **예측 가능한 동작**

   - 개발자가 결과를 받은 후 DOM이 변해도 결과가 변하지 않음
   - 디버깅과 테스트가 용이

3. **새로운 API의 이점**
   - 기존 API와 달리 하위 호환성 부담이 없었음
   - 더 나은 설계 선택이 가능했음

**비교 예시:**

```javascript
// 전통적 방식 (live)
const liveItems = document.getElementsByClassName("item");
console.log(liveItems.length); // 3

document.body.appendChild(createItemElement());
console.log(liveItems.length); // 4 (자동 업데이트)

// 모던 방식 (static)
const staticItems = document.querySelectorAll(".item");
console.log(staticItems.length); // 3

document.body.appendChild(createItemElement());
console.log(staticItems.length); // 3 (변하지 않음)

// 새로 조회하면 반영됨
const updatedItems = document.querySelectorAll(".item");
console.log(updatedItems.length); // 4
```

### 결론: 웹 표준의 진화

NodeList와 HTMLCollection의 분리는 **의도된 설계**라기보다는 **웹 표준의 점진적 진화** 과정에서 자연스럽게 발생한 결과입니다.

처음부터 다시 설계한다면 하나의 통일된 컬렉션 타입으로 만들었을 가능성이 높지만, **하위 호환성**이라는 웹의 핵심 원칙 때문에 기존 API들을 그대로 유지해야 했습니다.

> 💡 **유사한 사례들**
>
> 웹 플랫폼에는 이러한 역사적 유산이 많습니다:
>
> - JavaScript의 `Date` 객체 (월이 0부터 시작, 날짜는 1부터 시작)
> - `typeof null === 'object'` (초기 구현 버그가 표준이 됨)
> - `document.all` (falsy한 object)
>
> 이들은 모두 **"웹을 망가뜨리지 않기(Don't break the web)"** 원칙의 결과입니다.

---

## 실무 가이드

이론적 이해를 넘어, 실무에서 어떻게 활용해야 하는지 구체적인 가이드를 제시합니다.

### 언제 무엇을 사용할까?

**대부분의 경우: `querySelectorAll()` 사용 (권장)**

```javascript
// ✅ 추천: 정적 NodeList
const items = document.querySelectorAll(".item");

// 장점:
// - forEach() 사용 가능
// - 정적이라 예측 가능
// - 성능 우수
// - 복잡한 CSS 선택자 지원

items.forEach((item) => {
  item.addEventListener("click", handleClick);
});
```

**실시간 추적이 필요한 경우만: `getElementsByClassName()` 등**

```javascript
// ⚠️ 신중히 사용: 동적 HTMLCollection
const liveItems = document.getElementsByClassName("item");

// 사용 시나리오:
// - 실시간으로 변하는 리스트를 계속 추적해야 할 때
// - 메모리 효율이 중요한 대규모 DOM에서
// - 하지만 대부분의 경우 재조회하는 게 더 명확함

// 예: 실시간 필터링 UI
function updateVisibleItems() {
  const visibleItems = document.getElementsByClassName("visible");
  statusBar.textContent = `표시된 항목: ${visibleItems.length}개`;
  // visibleItems는 항상 최신 상태 반영
}
```

**노드 타입 구분이 필요한 경우: `childNodes`**

```javascript
// Element와 Text 노드를 모두 다뤄야 할 때
const allNodes = element.childNodes;

allNodes.forEach((node) => {
  if (node.nodeType === Node.TEXT_NODE) {
    console.log("텍스트:", node.textContent.trim());
  } else if (node.nodeType === Node.ELEMENT_NODE) {
    console.log("요소:", node.tagName);
  }
});

// vs. Element만 필요한 경우
const elements = element.children; // HTMLCollection
```

### 성능 고려사항

**1. Live Collection 반복 시 주의**

```javascript
// ❌ 나쁜 예: length를 매번 재계산
const items = document.getElementsByClassName("item");
for (let i = 0; i < items.length; i++) {
  // length가 매번 DOM 쿼리
  console.log(items[i]);
}

// ✅ 좋은 예: length를 캐싱
const items = document.getElementsByClassName("item");
const len = items.length; // 한 번만 계산
for (let i = 0; i < len; i++) {
  console.log(items[i]);
}

// ✅ 더 좋은 예: 정적 NodeList 사용
const items = document.querySelectorAll(".item");
items.forEach((item) => console.log(item));
```

**2. 대량의 DOM 조작 시**

```javascript
// ❌ 나쁜 예: live collection으로 DOM 수정
const items = document.getElementsByClassName("item");
for (let i = 0; i < items.length; i++) {
  // 매 반복마다 DOM 변경이 live collection에 영향
  items[i].className = "new-item";
}

// ✅ 좋은 예: 배열로 변환 후 작업
const items = [...document.getElementsByClassName("item")];
items.forEach((item) => {
  item.className = "new-item";
});

// ✅ 더 좋은 예: DocumentFragment 활용
const fragment = document.createDocumentFragment();
const items = document.querySelectorAll(".item");
items.forEach((item) => {
  const clone = item.cloneNode(true);
  clone.className = "new-item";
  fragment.appendChild(clone);
});
container.appendChild(fragment); // 한 번에 DOM 삽입
```

**3. 선택자 복잡도**

```javascript
// ⚠️ getElementsByClassName은 단순 클래스만
const items1 = document.getElementsByClassName("item");

// ✅ querySelectorAll은 복잡한 선택자 가능
const items2 = document.querySelectorAll(".container > .item:not(.disabled)");
const items3 = document.querySelectorAll('[data-status="active"]');
const items4 = document.querySelectorAll(".item:nth-child(odd)");
```

**실용적인 유틸리티 함수:**

```javascript
// 어떤 컬렉션이든 안전하게 배열로 변환
function toArray(collection) {
  return Array.from(collection);
}

// 컬렉션 타입에 관계없이 반복 처리
function forEachNode(collection, callback) {
  Array.from(collection).forEach(callback);
}

// 사용
const items = document.getElementsByClassName("item"); // HTMLCollection
forEachNode(items, (item) => {
  console.log(item.textContent);
});
```

---

## 정리

### 핵심 요약

| 관점            | NodeList                                                                   | HTMLCollection             |
| --------------- | -------------------------------------------------------------------------- | -------------------------- |
| **포함 노드**   | 모든 노드 타입 (Element, Text, Comment 등)                                 | Element 노드만             |
| **동적 특성**   | 메서드에 따라 다름<br>- `querySelectorAll()`: 정적<br>- `childNodes`: 동적 | 항상 동적 (live)           |
| **배열 메서드** | `forEach()` 지원                                                           | `forEach()` 미지원         |
| **유사배열**    | ✅ (`length`, 인덱스 접근)                                                 | ✅ (`length`, 인덱스 접근) |
| **Iterable**    | ✅ (`[...]`, `for...of`)                                                   | ✅ (`[...]`, `for...of`)   |
| **성능**        | 정적일 경우 우수                                                           | 실시간 추적 비용 존재      |

### 실무 권장사항

1. **기본적으로 `querySelectorAll()` 사용**

   - 정적이라 예측 가능
   - `forEach()` 바로 사용 가능
   - 복잡한 선택자 지원

2. **Live collection이 정말 필요한 경우만 `getElementsByClassName()` 등 사용**

   - 실시간 DOM 추적이 필수적일 때
   - 사용 시 배열로 변환하여 안전하게 처리

3. **모든 노드 타입이 필요하면 `childNodes`**

   - Text 노드나 Comment 노드도 다뤄야 할 때

4. **성능이 중요한 경우**
   - Live collection의 `length`는 캐싱
   - 대량 DOM 조작 전에 배열로 변환
   - DocumentFragment 활용

### 역사적 이해

NodeList와 HTMLCollection의 분리는 웹 표준의 점진적 진화 과정에서 발생한 결과입니다. 처음부터 다시 설계한다면 하나로 통일했겠지만, **"웹을 망가뜨리지 않기(Don't break the web)"** 원칙에 따라 기존 API를 유지하면서 새로운 API를 추가하는 방식으로 발전해 왔습니다.

현대 웹 개발에서는 대부분 `querySelectorAll()`을 사용하지만, 레거시 코드를 다루거나 라이브러리를 개발할 때는 두 컬렉션의 차이를 정확히 이해하는 것이 중요합니다.
