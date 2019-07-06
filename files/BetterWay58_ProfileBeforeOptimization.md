## Better Way 58. 최적화하기 전에 프로파일하자

#### 295쪽

* Created : 2019/07/06
* Modified: 2019/07/06

<br>

## 1. 프로파일링을 통한 성능 개선

파이썬의 동적 특징은 런타임 성능에서 놀랄만한 동작을 보여준다. 느릴 것이라고 예상한 연산이 실제로는 엄청나게 빠르다거나(문자열 처리, 제너레이터), 빠를 것이라고 예상한 언어의 특성은 실제로 매우 느리다(속성 접근, 함수 호출). 파이썬 프로그램을 느리게 만드는 요인이 불분명할 수도 있다.  

**가장 좋은 방법은 최적화하기 전에 직관을 무시하고 직접 프로그램의 성능을 측정해보는 것이다.** 파이썬은 프로그램의 어느 부분이 실행 시간을 소비하는지 파악할 수 있도록 `내장 프로파일러`를 제공한다. 프로파일러를 이용하면 문제의 가장 큰 원인에 최적화 노력을 최대한 집중할 수 있고, 속도에 영향을 주지 않는 부분은 무시할 수 있다.

예를 들어 프로그램의 알고리즘이 느린 이유를 알고 싶다고 하자. 다음은 삽입 정렬로 데이터 리스트를 정렬하는 함수다.

```python
def insertion_sort(data):
    result = []
    for value in data:
        insert_value(result, value)
    return result
```

알다시피 **삽입 정렬의 핵심 메커니즘은 각 데이터의 삽입 지접을 찾는 함수다.** 다음은 극히 비효율적인 *insert\_value* 함수로, 입력 배열을 순차적으로 스캔한다.

```python
def insert_value(arr, value):
    for i, existing in enumerate(arr):
        if existing > value:
            arr.insert(i, value)
            return
    arr.append(value)
```

*insertion\_sort* 와 *insert\_value* 를 프로파일하려고 난수로 구성된 데이터 집합을 생성하고, 프로파일러에 넘길 test 함수를 정의한다.

```python
from random import randint

MAX_SIZE = 10 ** 4
data = [randint(MAX_SIZE) for _ in range(MAX_SIZE)]
test = lambda: insertion_sort(data)
```

<br>

이제 프로파일러를 사용해보자. 파이썬은 두 가지 내장 프로파일러를 제공하는데, 하나는 순수 파이썬 모듈(profile)이며 다른 하나는 C 확장 모듈(cProfile)이다. **후자는 프로파일링 동안에 프로그램의 성능에 미치는 영향을 최소화할 수 있어서 더 좋다. 순수 파이썬 프로파일러는 결과를 왜곡할 정도로 부하가 크다.** [관련 문서](https://docs.python.org/3/library/profile.html)는 여기.

cProfile 모듈의 Profile 객체를 생성하고 runcall 메소드로 테스트 함수를 실행해보자.

```python
from cProfile import Profile

profiler = Profile()
profiler.runcall(test)
```

테스트 함수의 실행이 끝나면 내장 모듈 pstats의 Stats 클래스로 함수의 성능 통계를 뽑을 수 있다. pstats는 (아마) 'Print Statistics'의 약자로 프로파일링된 파이썬 코드에 대한 보고서를 출력하는 모듈이라고 한다. 이 모듈의 Stats 객체의 다양한 메소드를 이용하면 프로파일 정보를 선택하고 정렬하는 방법을 조절해서 관심 있는 정보만 볼 수 있다.

```python
from pstats import Stats

stats = Stats(profiler)
stats.strip_dirs()
stats.sort_stats('cumulative')
stats.print_stats()
```

결과는 함수로 구성된 정보의 테이블이다. 데이터 샘플은 runcall 메소드가 실행되는 동안 프로파일러가 활성화되어 있을 때만 얻어온다.

```
      20003 function calls in 3.985 seconds

Ordered by: cumulative time

ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     1    0.000    0.000    3.985    3.985 <ipython>:21(<lambda>)
     1    0.012    0.012    3.985    3.985 <ipython>:1(insertion_sort)
 10000    3.925    0.000    3.973    0.000 <ipython>:8(insert_value)
  9995    0.048    0.000    0.048    0.000 {method 'insert' of 'list' objects}
     5    0.000    0.000    0.000    0.000 {method 'append' of 'list' objects}
     1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
```

프로파일러 통계 칼럼의 의미를 간략히 알아보자.

* ncalls: 프로파일링 주기 동안 함수 호출 횟수
* tottime: 함수가 실행되는 동안 소비한 초 단위의 시간으로, 다른 함수 호출을 실행하는 데 걸린 시간은 배제한다.
* tottime percall: 함수를 호출하는 데 걸린 평균 시간이며 초 단위다. 다른 함수의 호출 시간은 배제한다. tottime을 ncalls로 나눈 값이다.
* cumtime: 함수를 실행하는 데 걸린 초 단위 누적 시간이며, 다른 함수를 호출하는 데 걸린 시간도 포함한다.
* cumtime percall: 함수를 호출할 때마다 걸린 시간에 대한 초 단위 평균 시간이며, 다른 함수를 호출하는 데 걸린 시간도 포함한다. cumtime을 ncalls로 나눈 값이다.

**프로파일러 통계를 보면 테스트에서 CPU를 가장 많이 사용한 부분은 *insert\_value* 함수에서 소비한 누적 시간이라는 것을 알 수 있다.**

<br>

이번에는 내장 모듈 bisect를 사용하도록 *insert\_value* 를 재정의한다.

```python
from bisect import bisect_left


def insert_value(arr, value):
    i = bisect_left(arr, value)
    arr.insert(i, value)
```

다시 프로파일러를 실행하여 새 프로파일러 통계를 생성한다. 새로운 함수는 더 빨라졌고, 누적 시간은 이전의 함수에 비해 거의 100배 이상 줄었다.


```
      30003 function calls in 0.084 seconds

Ordered by: cumulative time

ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     1    0.000    0.000    0.084    0.084 <ipython>:27(<lambda>)
     1    0.010    0.010    0.084    0.084 <ipython>:1(insertion_sort)
 10000    0.013    0.000    0.074    0.000 <ipython>:10(insert_value)
 10000    0.042    0.000    0.042    0.000 {method 'insert' of 'list' objects}
 10000    0.019    0.000    0.019    0.000 {built-in method _bisect.bisect_left}
     1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
```


<Br>

## 2. 다른 사례

때로는 전체 프로그램을 프로파일할 때 `공통` 유틸리티 함수에서 대부분의 실행 시간을 소비할 수도 있다. 프로파일러의 기본 출력은 유틸리티 함수가 프로그램의 다른 부분에서 얼마나 많이 호출되는지는 보여주지 않기 때문에 이해하기가 어렵다.

예를 들어 다음 *my\_utility* 함수는 프로그램에 있는 다른 두 함수에서 반복적으로 호출된다.


```python
def common_utility(a, b):
    for _ in range(10000):
        a * b

def first_func():
    for _ in range(1000):
        common_utility(4, 5)


def second_func():
    for _ in range(10):
        common_utility(1, 3)


def my_program():
    for _ in range(20):
        first_func()
        second_func()
```

이 코드를 프로파일하고 앞서 사용한 *print\_stats* 출력을 사용하면 이해하기 어려운 통계 결과가 나온다.


```
      20242 function calls in 0.014 seconds

Ordered by: cumulative time

ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     1    0.000    0.000    0.014    0.014 <ipython>:15(my_program)
    20    0.009    0.000    0.013    0.001 <ipython>:5(first_func)
 20200    0.044    0.000    0.004    0.000 <ipython>:1(common_utility)
    20    0.000    0.000    0.000    0.000 <ipython>:10(second_func)
     1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
```

*common\_utility* 함수가 대부분의 실행 시간을 소비하는 원인이라는 게 명확하지만, **이 함수가 왜 이렇게 많이 호출되는지는 명확하게 알기 어렵다.** 이 함수는 여러 함수에서 공통적으로 쓰이지 않기 때문이다. 전체 호출 횟수에서(ncalls) 다른 여러 함수들의 호출 지분을 알기 어렵다는 말과도 같다. 프로그램 코드에서 찾는다면 파악할 수도 있겠지만 결코 좋은 방법은 아니다.  

다행히 Stats 클래스는 이런 상황에도 대처할 수 있는, 호출자를 찾는 메소드도 지원한다.


```python
stats.print_callers()
```

메소드를 통해 반환된 프로파일러 통계 테이블은 호출된 함수를 왼쪽에 보여주며, 누가 이런 호출을 하는지를 오른쪽에 보여준다. 표를 통해 *common\_utility* 가 *first\_func* 에서 가장 많이 사용되었음을 명확하게 보여준다.


```
   Ordered by: cumulative time

Function                                           was called by...
                                                       ncalls  tottime  cumtime
<ipython:16(my_program)     <- 
<ipython:6(first_func)      <-      20    0.017    0.060  <ipython>:16(my_program)
<ipython:1(common_utility)  <-   20000    0.043    0.043  <ipython>:6(first_func)
                                   200    0.000    0.000  <ipython>:11(second_func)
<ipython:11(second_func)    <-      20    0.000    0.001  <ipython>:16(my_program)
{method rofiler' objects}   <- 
```

<br>

## 3. 핵심 정리

* 성능 저하를 일으키는 원인이 때로는 불분명하므로 파이썬 프로그램을 최적화하기 전에 프로파일해야 한다.
* cProfile이 더 정확한 프로파일링 정보를 제공하는 내장 모듈이므로 이것을 사용하자.
* Profile 객체의 runcall 메소드는 함수 호출 트피를 프로파일하는 데 필요한 모든 기능을 제공한다.
* Stats 객체는 프로그램 성능을 이해하는 데 필요한 프로파일링 정보를 선택하고 출력하는 기능을 제공한다.
