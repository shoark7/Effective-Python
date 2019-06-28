## Better Way 46. 내장 알고리즘과 자료구조를 사용하자

#### 237쪽

* Created : 2019/06/28
* Modified: 2019/06/28

<br>

## 1. 기본 자료구조의 한계

많은 데이터를 처리하는 프로그램을 구현할 때 기본 내장 자료구조(list, tuple, dict, set)을 사용하다보면 결국 성능의 한계에 다다르게 된다. 이는 이 자료구조들의 결함 때문이라기 보다는 기본 내장 자료구조이기 때문에 성능을 위해 최적화되지 않고 lightweight한 성격을 지니기 때문이다. 즉 **이들은 사용하기 쉽고 무게도 가볍지만, 많은 데이터를 다루고 성능이 중요한 상황일 때 관련 알고리즘들의 성능이 매우 뛰어나지는 않다.** 파이썬의 다른 내장 자료구조나 알고리즘 등도 이런 성격을 띤다.

하지만 때로는 성능을 중요시해야 하는 경우가 생기고 다행히도 파이썬 표준 라이브러리는 필요한 만큼 많은 알고리즘과 자료구조를 갖추고 있다. 꼭 성능 때문이 아니더라도 이런 공통 알고리즘과 자료구조를 사용하면 삶이 더 윤택해진다.

오늘 이 시간에는 파이썬이 갖추고 있는 수많은 다른 자료구조 중에서도 특히 쓸모 있는 몇 가지를 살펴보도록 한다.

<br>

## 2. Double Ended Queue

내장 collections 모듈의 [deque](https://docs.python.org/3/library/collections.html#collections.deque) 자료구조는 Double Ended Queue다. 즉, 양쪽 끝이 열러 있는 큐로서, 이 자료구조는 큐의 양쪽 끝에서 아이템을 삽입하거나 삭제할 때 항상 일정한 시간이 걸리는 연산을 제공한다. 이와 같은 기능은 FIFO 큐를 만들 때 이상적이다.

```python
from collections import deque

fifo = deque()
fifo.append(1)
print(fifo.popleft())

1
```

물론 이런 작업은 내장 `list`를 써도 얼마든지 할 수 있다. 하지만 **리스트가 자신의 오른쪽 끝에 원소를 추가, 삭제하는 데는 O(1)에 해결할 수 있는 데 반해, 왼쪽 끝에 원소를 추가, 삭제하는 데는 O(n)의 시간복잡도가 든다.** 이는 리스트의 중요한 한계로 따라서 list를 FIFO 큐로 쓰는 것은 성능이 중요할 때는 좋은 선택이 아니다.


<br>

## 3. 정렬된 딕셔너리

알다시피, 내장 `dict`는 키가 정렬되어 있지 않다. 즉, 같은 키와 값을 담은 dict를 순회해도 다른 순서가 나올 수 있다는 의미다. 이런 동작은 딕셔너리의 빠른 해시테이블을 구현하는 방식이 만들어낸 뜻밖의 부작용이다.

**collections 모듈의 [OrderedDict](https://docs.python.org/3/library/collections.html#collections.OrderedDict) 클래스는 키가 삽입된 순서를 유지하는 특별한 딕셔너리다.** OrderedDict는 내장 dict의 서브클래스로서 이름에서부터 유추할 수 있듯이 OrderedDict의 키를 순회하는 것은 예상 가능한 동작이다. 따라서 모든 코드를 확정하고 만들 수 있으므로 테스팅과 디버깅을 아주 간단하게 할 수 있다.


```python
from collections import OrderedDict

a = OrderedDict()
a['foo'] = 1
a['bar'] = 2

b = OrderedDict()
b['foo'] = 'red'
b['bar'] = 'blue'


for v1, v2 in zip(a.values(), b.values()):
    print(v1, v2)


1 red
2 blue
```

<br>

## 4. 기본값이 설정된 딕셔너리

딕셔너리의 중요한 사용처 중 하나는 빈도를 관리하고 추적하는 작업이다. 이때 한 가지 문제점이 따라오는데, **딕셔너리에서 어떤 키가 이미 존재한다고 가정할 수 없다는 점이다.** 이 문제 때문에 딕셔너리에 저장된 카운터를 증가시키는 것처럼 간단한 작업도 코드가 지저분해진다.

```python
sentence = "I wanna be a doctor"
counter = {}

for c in sentence:
    if c.isalpha():
        # 다음 두 줄이 깔끔하지 못하다
        if c not in counter:
            counter[c] = 0
        counter[c] += 1

print(counter)

{'I': 1, 'w': 1, 'a': 3, 'n': 2, 'b': 1, 'e': 1, 'd': 1, 'o': 2, 'c': 1, 't': 1, 'r': 1}
```

**collections의 [defaultdict](https://docs.python.org/3/library/collections.html#collections.defaultdict) 자료구조는 키가 존재하지 않으면 자동으로 기본값을 저장하도록 하여 이런 작업을 간소화한다. 할 일은 그저 키가 없을 때마다 기본값을 반환할 함수를 제공하는 것뿐이다.**o

```python
from collections import defaultdict

sentence = "I wanna be a doctor"
counter = defaultdict(int)

for c in sentence:
    if c.isalpha():
        counter[c] += 1

print(counter)

defaultdict(<class 'int'>, {'I': 1, 'w': 1, 'a': 3, 'n': 2, 'b': 1, 'e': 1, 'd': 1, 'o': 2, 'c': 1, 't': 1, 'r': 1})
```

**defaultdict는 인자로 함수를 받는데, 만약 찾는 키가 없으면 제공받은 함수의 결과가 키의 기본값으로 설정된다.** int 함수를 인자없이 쓰면 0이 반환되기 때문에 딕셔너리에 키가 없으면 자동으로 0이 할당된 뒤 다시 1이 추가된다.(_counter[c] += 1_)


<br>

## 5. 힙 큐

**힙(heap)은 우선순위 큐(priority queue)를 유지하는 유용한 자료구조다.** 이 자료구조는 자료구조학의 진정한 효자로서 잘 모르면 [관련 문서](https://en.wikipedia.org/wiki/Heap_(data_structure))를 꼭 확인하기 바란다.

힙과 관련된 알고리즘을 파이썬에서도 제공하는데, heapq 모듈은 표준 list 타입으로 힙을 생성하는 heappush, heappop, nsmallest 등의 함수를 제공한다.

```python
from heapq import heappop, heappush

a = []
heappush(a, 5)
heappush(a, 3)
heappush(a, 7)
heappush(a, 4)

print(heappop(a), heappop(a), heappop(a), heappop(a))

3 4 5 7
```

**파이썬의 heap은 최소값 힙(mean heap)으로서, 값을 하나씩 빼낼 때마다 최소값을 O(log n)의 시간복잡도로 추출할 수 있다.** 표준 파이썬 리스트로 같은 동작을 수행하면 시간이 선형적으로 증가하기 때문에 heap은 최소값(또는 최대값)을 추가, 삭제하는 연산에 효율적이다.

<br>

## 6. 바이섹션

list에서 아이템을 검색하는 작업은 index 메소드를 호출할 때 리스트의 길이에 비례한 선형적 시간이 걸린다.


```python
x = list(range(10 ** 6))
i = x.index(991234)
```

[bisect 모듈](https://docs.python.org/3/library/bisect.html)은 정렬된 아이템 시퀀스를 대상으로한 효율적인 바이너리 검색을 제공하는 bisect\_left 같은 함수를 제공한다. bisect\_left가 반환한 인덱스는 시퀀스에 들어간 값의 삽입 지점이다.

```python
from bisect import bisect_left

x = list(range(10 ** 6))
i = bisect_left(x, 991234)
print(i)

991234
```

**바이너리 검색의 복잡도는 로그 형태로 증가한다.** 다시 말해 아이템 백만 개를 담은 리스트를 bisect로 검색할 때 걸리는 시간은 아이템 14개(log2 1000000)를 담은 리스트를 index로 순차 검색할 때 걸리는 시간과 거의 같다.


<br>

## 7. 이터레이터 도구

**내장 모듈 [itertools](https://docs.python.org/3/library/itertools.html)는 이터레이터를 구성하거나 이터레이터와 상호작용하는 데 유용한 함수를 다수 포함한다.** 파이썬 2에서는 이런 기능을 모두 이용하진 못하지만, 모듈 문서에 있는 예제를 참고하면 간단하게 만들 수 있다. 더 자세한 정보는 itertools 모듈에 헬핑을 하면 확인해볼 수 있다.

itertools에 있는 함수는 크게 세 가지 범주로 나눌 수 있다.

* 이터레이터 연결
  - chain: 여러 이터레이터를 순차적인 이터레이터 하나로 결합한다.
  - cycle: 이터레이터의 아티메을 영원히 반복한다.
  - tee: 이터레이터 하나를 병렬 이터레이터 여러 개로 나눈다.
  - zip\_longest: 길이가 서로 다른 이터레이터들에도 잘 동작하는 내장 함수 zip의 변형이다.
* 이터레이터에서 아이템 필터링
  - islice: 복사 없이 이터레이터를 숫자로 된 인덱스로 슬라이스한다.
  - takewhile: 서술 함수(predicate function)가 True를 반환하는 동안 이터레이터의 아이템을 반환한다.
  - dropwhile: 서술 함수가 처음으로 False를 반환하고 나면 이터레이터의 아이템을 반환한다.
  - filterfalse: 서술 함수가 False를 반환하는 이터레이터의 모든 아이템을 반환한다. 내장 함수 filter의 반대기능을  한다.
* 이터레이터에 있는 아이템들의 조합
  - product: 이터레이터에 있는 아이템들의 카르테시안 곱을 반환한다. 깊게 중첩된 리스트 컴프리헨션에 대한 훌륭한 대안이다.
  - permutations: 이터레이터에 있는 아이템을 담은 길이 N의 순서 있는 순열을 반환한다.
  - combinations: 이터레이터에 있는 아이템을 중복되지 않게 담은 길이 N의 순서 없는 조합을 반환한다.

<br>

itertools에는 이것말고도 다른 기능이 더 많고 나도 다 써보지도 않았다. 하지만 몇몇은 실제 개발에서 정말 유용할 수 있어서 이 모듈은 살펴볼 가치가 있다.

<br>

## 8. 핵심 정리

* 알고리즘과 자료구조를 표현하는 데는 파이썬의 내장 모듈을 사용하자.
* 이 기능들을 직접 재구현하지는 말자. 올바르게 만들기가 어렵기 때문이다.
