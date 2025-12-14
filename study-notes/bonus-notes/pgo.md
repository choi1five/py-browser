# Profile-Guided Optimization (PGO) 가이드

## PGO란 무엇인가?

**Profile-Guided Optimization (PGO)**는 실제 실행 데이터를 기반으로 컴파일러가 최적화를 수행하는 기법입니다.

### 핵심 아이디어

일반적인 컴파일러 최적화는 **정적 분석**만 사용합니다:

- 코드만 보고 판단
- 실제 실행 패턴을 모름
- 모든 경로를 동등하게 취급

PGO는 **동적 프로파일링**을 추가합니다:

- 실제로 실행해서 데이터 수집
- 자주 실행되는 코드 경로 파악
- "핫 패스(hot path)"를 집중 최적화

### 왜 필요한가?

```cpp
// 예시 코드
if (isRareCase) {  // 컴파일러는 비율을 모름
    rareFunction();
} else {
    commonFunction();
}
```

**컴파일러의 한계:**

- `isRareCase`가 얼마나 자주 true인지 알 수 없음
- 50:50으로 가정하고 최적화

**실제 실행 결과:**

- `isRareCase`는 0.01%만 true
- `commonFunction()`이 99.99% 실행됨

**PGO의 해결:**

- 실행 데이터로 이를 파악
- `commonFunction()` 경로를 최적화

---

## PGO 작동 원리

### 3단계 프로세스

```
[소스 코드]
    ↓
[1단계] Instrumentation Build
    ↓
[실행 & 프로파일 수집]
    ↓
[2단계] 프로파일 데이터 생성
    ↓
[3단계] Optimized Build
    ↓
[최종 바이너리]
```

### 1단계: Instrumentation Build

**목적:** 실행 데이터를 수집할 수 있는 특수 바이너리 생성

```bash
# 예시: LLVM/Clang 컴파일러
clang++ -fprofile-generate source.cpp -o instrumented_binary
```

**컴파일러가 하는 일:**

- 각 함수 시작 부분에 카운터 추가
- 분기문(if/switch)마다 카운터 추가
- 함수 호출마다 카운터 추가

**생성된 코드 (개념적):**

```cpp
// 원본 코드
void myFunction() {
    if (condition) {
        branchA();
    } else {
        branchB();
    }
}

// Instrumentation 후
void myFunction() {
    __profile_function_entry("myFunction");  // 추가됨

    if (condition) {
        __profile_branch_taken("myFunction_if_true");  // 추가됨
        branchA();
    } else {
        __profile_branch_taken("myFunction_if_false");  // 추가됨
        branchB();
    }
}
```

### 2단계: 프로파일 수집 (Runtime)

**실행:**

```bash
# Instrumented 바이너리 실행
./instrumented_binary

# 프로파일 데이터 파일 생성
# default.profraw 파일이 생성됨
```

**수집되는 데이터:**

- 각 함수가 몇 번 호출되었는가?
- 각 분기문에서 true/false 비율은?
- 각 루프가 평균 몇 번 반복되는가?
- 함수 호출 체인은?

**프로파일 데이터 예시:**

```
function: myFunction
  executed: 1,000,000 times
  branch_true: 1,000 times (0.1%)
  branch_false: 999,000 times (99.9%)
```

**프로파일 데이터 병합:**

```bash
# 여러 실행 결과를 하나로 병합
llvm-profdata merge -o merged.profdata *.profraw
```

### 3단계: Optimized Build

**최종 컴파일:**

```bash
clang++ -fprofile-use=merged.profdata source.cpp -o optimized_binary
```

**컴파일러가 하는 일:**

- 프로파일 데이터를 읽음
- 핫 패스를 파악
- 데이터 기반 최적화 적용

---

## PGO의 최적화 기법

### 1. 함수 인라이닝 (Function Inlining)

**프로파일 없이:**

```cpp
// 모든 함수 호출을 동등하게 취급
result = calculateSmallValue();  // 인라이닝 여부 모호
```

**PGO 적용:**

```cpp
// 프로파일: calculateSmallValue() 호출 빈도 = 초당 100만 번
// → 컴파일러가 인라이닝 결정
result = /* calculateSmallValue의 코드가 여기 직접 삽입 */;
```

**효과:**

- 함수 호출 오버헤드 제거
- 추가 최적화 기회 제공

### 2. 코드 배치 최적화 (Code Layout)

**CPU 캐시 활용:**

```
[메모리 배치]

PGO 없이:
[functionA] [functionB] [functionC] [functionD]
    ↓           ↓           ↓           ↓
  거의 실행   자주 실행   거의 실행   자주 실행

PGO 적용:
[functionB] [functionD] [functionA] [functionC]
    ↓           ↓           ↓           ↓
  자주 실행   자주 실행   거의 실행   거의 실행
```

**효과:**

- 자주 실행되는 코드를 연속된 메모리에 배치
- CPU 명령어 캐시 적중률 향상
- 캐시 미스 감소

### 3. 분기 예측 최적화 (Branch Prediction)

**프로파일 데이터:**

```
if (condition)  // true: 99%, false: 1%
```

**어셈블리 코드 배치:**

```asm
; PGO 없이 (true/false 동등하게 취급)
    test condition
    jz   false_branch    ; false면 점프
    ; true branch 코드
    jmp  end
false_branch:
    ; false branch 코드
end:

; PGO 적용 (true가 99%이므로)
    test condition
    jnz  true_branch     ; true면 점프 (순서 변경)
    ; false branch 코드 (거의 안 실행)
    jmp  end
true_branch:
    ; true branch 코드 (자주 실행)
end:
```

**효과:**

- CPU 분기 예측기가 올바른 예측을 하기 쉬움
- 파이프라인 스톨(stall) 감소

### 4. 루프 최적화

**프로파일 데이터:**

```cpp
for (int i = 0; i < n; i++) {  // 평균 반복: 5회
    process(i);
}
```

**최적화 결정:**

- 반복 횟수가 적으면 → 루프 언롤링(unrolling)
- 반복 횟수가 많으면 → 벡터화(vectorization)

### 5. 레지스터 할당

**우선순위:**

```cpp
// 프로파일: hotFunction은 초당 100만 번 호출
// → hotFunction 내 변수에 레지스터 우선 할당

void hotFunction() {
    int x = ...;  // 레지스터 할당 우선
    int y = ...;  // 레지스터 할당 우선
}

void coldFunction() {
    int a = ...;  // 메모리 사용 허용
    int b = ...;  // 메모리 사용 허용
}
```

---

## Chromium의 PGO 구현

### 빌드 설정 파일

**위치:**

- `build/config/compiler/pgo/pgo.gni`
- `chrome/build/pgo_profiles/`

**chrome_pgo_phase 값:**

- `0`: PGO 사용 안 함
- `1`: 프로파일 생성 모드 (instrumentation)
- `2`: 프로파일 사용 모드 (optimization)

### Chromium의 3단계 프로세스

#### 1단계: Instrumentation Build

```bash
# GN 설정
gn gen out/PGO_Instrument --args='
  chrome_pgo_phase = 1
  enable_resource_allowlist_generation = false
  is_official_build = true
  symbol_level = 0
  use_remoteexec = true
'

# 빌드
ninja -C out/PGO_Instrument chrome
```

**생성 결과:**

- 프로파일링 코드가 삽입된 Chrome 바이너리
- 실행하면 `.profraw` 파일들이 생성됨

#### 2단계: 프로파일 수집

**Chromium의 방법:**

```bash
# 자동화된 벤치마크 실행
python3 tools/pgo/generate_profile.py -C out/PGO_Instrument
```

**generate_profile.py가 하는 일:**

1. **Telemetry 프레임워크 사용**

   - Chromium의 성능 측정 도구
   - 실제 사용자 시나리오 시뮬레이션

2. **대표적인 웹사이트 방문**

   - 상위 1000개 웹사이트 자동 방문
   - 페이지 로딩
   - 스크롤링
   - JavaScript 실행
   - 사용자 상호작용 시뮬레이션

3. **다양한 워크로드 실행**

   ```python
   # 예시 워크로드 (개념적)
   workloads = [
       'page_load',      # 페이지 로딩
       'scroll',         # 스크롤
       'javascript',     # JS 실행
       'rendering',      # 렌더링
       'video_playback', # 비디오 재생
   ]
   ```

4. **프로파일 데이터 수집**
   - 각 워크로드 실행마다 `.profraw` 파일 생성
   - 모든 데이터를 `profile.profdata`로 병합

**Android의 경우:**

```bash
python3 tools/pgo/generate_profile.py \
  -C out/PGO_Instrument \
  --android-browser android-trichrome-chrome-google-bundle
```

#### 3단계: Optimized Build

```bash
# GN 설정
gn gen out/PGO_Optimized --args='
  enable_resource_allowlist_generation = false
  is_official_build = true
  symbol_level = 0
  use_remoteexec = true
  pgo_data_path = "//out/PGO_Instrument/profile.profdata"
'

# 최종 빌드
ninja -C out/PGO_Optimized chrome
```

**결과:**

- 프로파일 데이터 기반으로 최적화된 Chrome
- 약 10-20% 성능 향상

### 플랫폼별 프로파일 관리

**프로파일 저장 위치:**

```
chrome/build/pgo_profiles/
├── android-arm64.pgo.txt      # Android ARM64용
├── win64.pgo.txt              # Windows 64bit용
├── linux.pgo.txt              # Linux용
└── mac-arm64.pgo.txt          # macOS Apple Silicon용
```

**프로파일 파일 내용 예시:**

```
# android-arm64.pgo.txt
chrome-android-arm64-1a2b3c4d5e6f.profdata
```

**프로파일 다운로드:**

```python
# .gclient 파일에 추가
solutions = [
  {
    "custom_vars": {
      "checkout_pgo_profiles": True,  # PGO 프로파일 다운로드
    },
  },
]
```

```bash
# 프로파일 다운로드
gclient runhooks
```

### CI/CD 자동화

**Chromium의 PGO 봇:**

- `android-arm64-pgo` (Android용)
- `win64-pgo` (Windows용)
- 등등...

**자동화 프로세스:**

1. 코드 변경사항 커밋
2. PGO 봇이 자동 실행
3. 새 프로파일 생성
4. Google Cloud Storage에 업로드
5. 프로파일 파일 이름 업데이트
6. 다음 빌드부터 새 프로파일 사용

---

## 실제 사용 예시

### 예시 1: 렌더링 파이프라인 최적화

**시나리오:**

```cpp
// Blink 렌더링 엔진의 레이아웃 코드
void LayoutObject::Layout() {
    if (needsLayout()) {           // 프로파일: 95% true
        performLayout();
    } else {
        skipLayout();               // 프로파일: 5% 실행
    }
}
```

**PGO 최적화:**

- `performLayout()` 경로를 인라이닝
- `skipLayout()` 경로는 함수 호출로 유지
- 코드 배치: `performLayout()` 코드를 먼저 배치

**성능 향상:**

- 레이아웃 계산 속도 15% 향상
- 페이지 렌더링 시간 단축

### 예시 2: JavaScript 엔진 (V8) 최적화

**시나리오:**

```cpp
// V8의 타입 체크 코드
if (object->IsJSObject()) {        // 프로파일: 90% true
    HandleJSObject(object);
} else if (object->IsSmi()) {      // 프로파일: 8% true
    HandleSmi(object);
} else {                            // 프로파일: 2% true
    HandleOther(object);
}
```

**PGO 최적화:**

- 분기 예측: JSObject 경로가 가장 빠르게 실행되도록 배치
- `HandleJSObject()` 함수 인라이닝
- 다른 경로는 콜드 코드로 분리

**성능 향상:**

- JavaScript 실행 속도 10% 향상

### 예시 3: 네트워크 스택 최적화

**시나리오:**

```cpp
// HTTP 요청 처리
void ProcessRequest(Request* req) {
    if (req->IsHTTPS()) {          // 프로파일: 85% true (HTTPS 사용률)
        HandleHTTPS(req);
    } else {
        HandleHTTP(req);
    }
}
```

**PGO 최적화:**

- HTTPS 경로 최적화
- TLS 핸드셰이크 관련 코드 인라이닝

---

## 트레이드오프

### 장점

✅ **실제 성능 향상**

- 10-20% 속도 향상 (Chrome 기준)
- 실제 사용 패턴 기반 최적화

✅ **런타임 비용 없음**

- 컴파일 타임에만 비용 발생
- 최종 바이너리는 추가 오버헤드 없음

✅ **자동화 가능**

- CI/CD 파이프라인에 통합 가능

### 단점

❌ **빌드 시간 증가**

- 2-3배 증가 (두 번 컴파일)
- Instrumentation 빌드 + Optimized 빌드

❌ **프로파일 수집 비용**

- 대표 워크로드 실행 필요
- 시간과 리소스 소모

❌ **프로파일 유지보수**

- 코드 변경 시 프로파일 재생성 필요
- 프로파일이 오래되면 효과 감소

❌ **워크로드 의존성**

- 프로파일 수집 시나리오와 실제 사용이 다르면 효과 감소
- 잘못된 프로파일은 오히려 성능 저하 가능

### 언제 사용해야 하나?

**적합한 경우:**

- 릴리즈 빌드
- 성능이 중요한 애플리케이션
- 사용 패턴이 명확한 경우
- CI/CD 인프라가 갖춰진 경우

**적합하지 않은 경우:**

- 개발 중 (빌드 시간 중요)
- 사용 패턴이 매우 다양한 경우
- 빠른 반복 개발이 필요한 경우

---

## 참고 자료

### Chromium 공식 문서

- [PGO Documentation](https://chromium.googlesource.com/chromium/src.git/+/master/docs/pgo.md)

### 컴파일러 문서

- [Clang PGO](https://clang.llvm.org/docs/UsersManual.html#profile-guided-optimization)
- [GCC PGO](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html)
- [MSVC PGO](https://docs.microsoft.com/en-us/cpp/build/profile-guided-optimizations)

### 관련 블로그

- [Chromium Blog: Chrome just got faster with PGO](https://blog.chromium.org/2020/08/chrome-just-got-faster-with-profile.html)
- [Chromium Blog: Making Chrome on Windows faster with PGO](https://blog.chromium.org/2016/10/making-chrome-on-windows-faster-with-pgo.html)
