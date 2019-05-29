## Better Way 28. 커스텀 컨테이너 타입은 collections.abc의 클래스를 상속받게 만들자

#### 126쪽

* Created : 2017/01/04
* Modified: 2019/05/29  

<br>

## 1. 컨테이너 상속의 쉬운 예: list

파이썬 프로그래밍의 핵심은 데이터를 담은 클래스를 정의하고 이 객체들이 연계되는 방법을 명시하는 일이다. 모든 파이썬 클래스는 일종의 컨테이너로, 속성과 기능을 함께 캡슐화한다. 파이썬은 데이터 관리용 내장 컨테이너 타입(list, tuple, set, dict)도 제공한다.

**Sequence처럼 쓰임새가 간단한 클래스를 설계할 때는 파이썬의 내장 list 타입에서 상속받으려고 하는 게 당연하다.** 멤버의 빈도를 세는 메소드를 추가로 갖춘 커스텀 list 타입을 생성한다고 해보자.(Sequence는 list, tuple 등 많은 선형 자료구조의 부모 클래스가 되는 추상클래스다.)


```python
class FrequencyList(list):
    def __init__(self, members=None):
        # list의 생성자는 iterable을 요구하기 때문에
        # 새 리스트에 인자가 주어지지 않으면 강제로 빈 리스트를 인자로 넘김
        # help(list) 참고
        if members is None:
            members = []
        super().__init__(members)

    def frequency(self):
        counts = {}
        for item in self: # 주목! self를 바로 받아 아이템에 접근할 수 있다.
            counts.setdefault(item, 0)
            counts[item] += 1
        return counts
```

_FrequencyList_ 는 list를 상속받아 리스트 본연의 기능은 모두 수행하면서, 빈도를 세는 _frequency_ 라는 메소드가 추가된 상황이다. **list에서 상속받아 서브클래스를 만들었으므로 list의 표준 기능을 모두 갖춰서 파이썬의 익숙한 시맨틱을 유지한다. 추가한 메소드로 필요한 커스텀 동작을 더할 수 있다.**

한번 테스트해보자.

```python
import random
from string import ascii_lowercase as LOWERS


foo = FrequencyList()

for _ in range(10):
    foo.append(random.choice(LOWERS))


print("First element of foo is", foo[0])
print("Frequency of foo is", foo.frequency())


First element of foo is h
Frequency of foo is {'h': 1, 'i': 2, 'o': 1, 'y': 1, 'f': 1, 'u': 1, 'z': 1, 'p': 1, 'x': 1}
# 구체적인 결과는 매 사용마다 변할 것임!
```

_FrequencyList_ 는 list를 상속받았기 때문에 list가 지원하는 append 메소드와 인덱싱이 모두 가능하다. 거기에 더해 우리가 추가한 _frequency_ 메소드 또한 무난히 잘 작동하는 것을 알 수 있었다.


<br>

## 2. 컨테이너 상속의 보다 어려운 예

list 상속만으로도 현실에서 필요한 많은 작업을 무난하게 시행할 수 있다. 하지만 더 복잡한 상황을 가정해보자. 선형 자료구조인 list의 서브 클래스는 아니지만 인덱스로 접근할 수 있게 해서 list처럼 보이는 객체를 제공하고 싶다고 하자.  

예를 들어 비선형 자료구조인 Binary Tree 클래스에 list나 tuple 같은 시퀀스 시맨틱을 제공하고 싶다고 하자. Binary Tree는 트리 자료구조에서 각 노드가 자식을 최대 왼쪽, 오른쪽 단 두 개만 갖는 자료구조로서 원소 추가, 삭제 동작에서 list보다 더 높은 효율을 보일 수 있다.

```python
class BinaryNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
```

이 클래스가 Sequence처럼 동작하게 하려면 어떻게 해야 할까? 알다시피 파이썬은 특별한 이름을 붙인 인스턴스 메소드로 컨테이너 동작을 구현한다.

list의 인덱싱을 예로 들어보자.

```python
bar = [1, 2, 3]
bar[0]
```

list의 첫 번째 원소를 구하는 간단한 인덱싱이다. 하지만 사실 이는 내부적으로 다음과 같은 메소드를 호출하는 문법이다.

```python
bar.__getitem__(0)
```

따라서, BinaryNode 클래스가 Sequence처럼 인덱싱을 지원하게 하려면 객체의 트리를 깊이 우선으로 탐색하는 \_\_getitem\_\_ 을 구현하면 된다.

```python
class IndexableNode(BinaryNode):
    def _search(self, count, index):
        # ...
        # 비선형 트리를 선형으로 직렬화했을 때의 인덱스 찾기
	# (found, count) 반환

    def __getitem__(self, index):
        found, _ = self._search(0, index)
        if not found:
            raise IndexError("Index out of range")
        return found.value
```

이 바이너리 트리는 평소처럼 생성하면 된다.

```python
tree = IndexableNode(
            10,
            left=IndexableNode(
                    5,
                    left=IndexableNode(2),
                    right=IndexableNode(6, right=IndexableNode(7))
            ),
            right=IndexableNode(15, left=IndexableNode(11))
)
```

트리는 Sequence와 달리 비선형 자료구조임에도 탐색은 물론이고 list처럼 인덱스로 접근할 수도 있다.

```python
print('LRR =', tree.left.right.right.value)
print('Index 0 =', tree[0])
print('Index 1 =', tree[1])
print('11 in the tree?', 11 in tree)
print('17 in the tree?', 17 in tree)
print('Tree is', list(tree))

LRR = 7
Index 0 = 2
Index 1 = 5
11 in the tree? True
17 in the tree? False
Tree is [2, 5, 6, 7, 10, 11, 15]
```

<br>

## 3. 위 방법의 문제점과 해결책

위와 같이 특정 메소드를 정의함으로써 Sequence 시맨틱을 지원할 수 있었다. 하지만 이 방법은 문제가 있는데 **Sequence 시맨틱에서 사용자가 기대하는 메소드는 인덱싱이 다가 아니며, _count_, _index_ 등의 메소드 등이 더 필요하기 때문이다.** 그러면 이 메소드들을 다 정의해줘야 하는 것인가? 커스텀 컨테이너 타입을 정의하는 일은 보기보다 어렵다.

```python
# __len__ 메소드 또한 시퀀스에서 사용자들이 흔히 시행할 수 있는 작업이다.
len(tree)

TypeError: object of type 'IndexableNode' has no len()
```

파이썬 세계의 이런 어려움을 피하기 위해 **내장 collections.abc 모듈은 각 컨테이너 타입에 필요한 일반적인 메소드를 모두 명시하는 추상 기반 클래스들을 정의한다.** 관련 [문서](https://docs.python.org/3/library/collections.abc.html)는 여기서 확인할 수 있다. 이 모듈은 list, tuple, set, dict 들과는 다른 방식의 메소드를 지원하기에 이들을 상속받는 것이 바람직하지 않은 커스텀 컨테이너를 지원하기 위해 있으며 여러 많은 컨테이너 타입에 필요한 일반적인 메소드를 모두 정의하는 추상 기반 클래스를 정의한다.(`abc`가 원래 'abstract base class'의 약자이다.)

**이 추상 기반 클래스에서 상속받아 서브클래스를 만들면, 만약 깜박 잊고 필수 메소드를 구현하지 않아도 파이썬이 뭔가 잘못되었다고 알려준다.**

```python
from collections.abc import Sequence

class BadType(Sequence):
    pass

foo = BadType()

TypeError: Can't instantiate abstract class BadType with abstract methods __getitem__, __len__
```

이 모듈 안에 있는 **_Sequence_ 추상클래스는 Sequence 시맨틱에 요구되는 필수 메소드들을 구현하지 않은 채 정의만하고 있는데, 이 _Sequence_ 를 상속하는 클래스를 정의한다는 것은 정의하는 클래스가 Sequence 시맨틱을 모두 지원하겠다는 선언을 하는 것이다.** 따라서 이 메소드들을 하나라도 구현하지 않으면 시맨틱이 충족되지 않았다고 파이썬에서 알려주기 때문에 요구되는 시맨틱을 모두 지원하는지 놓치지 않을 수 있다. 추가로 Sequence에 요구되는 필수 추상 메소드를 구현하면 별도로 작업하지 않아도 Sequence가 지원하는 index와 count 같은 부가적인 메소드를 자동으로 제공한다.

Set과 MutableMapping처럼 파이썬의 관례에 맞춰 구현해야 하는 특별한 메소드가 많은 더 복잡한 타입을 정의할 때 이런 추상 기반 클래스를 사용하는 이점은 더욱 커진다.

<br>

## 4. 핵심정리

* 쓰임새가 간단할 때는 list, dict와 같은 파이썬의 컨테이너 타입에서 직접 상속받게 하자.
* 커스텀 컨테이너 타입을 올바르게 구현하는 데 필요한 많은 메소드에 주의를 기울여야 한다.
* 커스텀 컨테이터 타입이 collections.abc에 정의된 인터페이스 클래스를 상속받게 만들어서 클래스가 필요한 인터페이스, 동작과 일치하게 하자.
