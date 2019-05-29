## Better Way 28. 커스텀 컨테이너 타입은 collections.abc의 클래스를 상속받게 만들자

#### 126쪽

* Created : 2017/01/04
* Modified: 2019/05/29  

<br>

## 1. 컨테이너 상속의 쉬운 예: list

파이썬 프로그래밍의 핵심은 데이터를 담은 클래스를 정의하고 이 객체들이 연계되는 방법을 명시하는 일이다. 모든 파이썬 클래스는 일종의 컨테이너로, 속성과 기능을 함께 캡슐화한다. 파이썬은 데이터 관리용 내장 컨테이너 타입(list, tuple, set, dict)도 제공한다.

**Sequence처럼 쓰임새가 간단한 클래스를 설계할 때는 파이썬의 내장 list 타입에서 상속받으려고 하는 게 당연하다.** 멤버의 빈도를 세는 메서드를 추가로 갖춘 커스텀 list 타입을 생성한다고 해보자.(Sequence는 list 등의 부모 클래스가 되는 추상클래스다.)


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

_FrequencyList_ 는 list를 상속받아 리스트 본연의 기능은 모두 수행하면서, 빈도를 세는 _frequency_ 라는 메서드가 추가된 상황이다. **list에서 상속받아 서브클래스를 만들었으므로 list의 표준 기능을 모두 갖춰서 파이썬의 익숙한 시맨틱을 유지한다. 추가한 메서드로 필요한 커스텀 동작을 더할 수 있다.**

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
# 결과는 매 사용마다 변할 것임!
```

_FrequencyList_ 는 list를 상속받았기 때문에 list가 지원하는 append 메소드와 인덱싱이 모두 가능하다. 거기에 더해 우리가 추가한 _frequency_ 메소드 또한 무난히 잘 작동하는 것을 알 수 있었다.


<br>

## 2. 보다 어려운 예

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

이 트리는 Sequence와 달리 비선형 자료구조임에도 탐색은 물ㄹ론이고 list처럼 인덱스로 접근할 수도 있다.

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

# Part 3.

위와 같이 특정 메소드를 정의함으로써 Sequence 시맨틱을 지원할 수 있었다. 하지만 이 방법은 문제가 있는데 Sequence 시맨틱에서 사용자가 기대하는 메소드는 인덱싱이 다가 아니며, _count_, _index_ 등의 메소드 등이 더 필요하기 때문이다. 그러면 이 메소드들을 다 정의해줘야 하는 것인가? 커스텀 컨테이너 타입을 정의하는 일은 보기보다 어렵다.

```python
len(tree)

TypeError: object of type 'IndexableNode' has no len()
```

파이썬 세계의 이런 어려움을 피하기 위해 **내장 collections.abc 모듈은 각 컨테이너 타입에 필요한 일반적인 메소드를 모두 제공하는 추상 기반 클래스들을 정의한다.** 관련 [문서](https://docs.python.org/3/library/collections.abc.html)는 여기서 확인할 수 있다. 이 모듈은 list, tuple, set, dict를 상속받는 것만으로 불충분한 컨테이너를 지원하기 위해 있으며 여러 많은 컨테이너 타입에 필요한 일반적인 메서드를 모두 제공하는 추상 기반 클래스를 정의한다.( abc가 원래 'abstract base class'의 약자이다. )

**이 추상 기반 클래스에서 상속받아 서브클래스를 만들면, 만약 깜박 잊고 필수 메서드를 구현하지 않아도 모듈이 뭔가 잘못되었다고 알려준다.**
"""

```python
from collections.abc import Sequence

class BadType(Sequence):
    pass

foo = BadType()

TypeError: Can't instantiate abstract class BadType with abstract methods __getitem__, __len__
```

이 모듈 안에 있는 **_Sequence_ 추상클래스는 Sequence 시맨틱에 요구되는 필수 메소드들을 구현하지 않은 채 정의만하고 있는데, 이 _Sequence_ 를 상속하는 클래스를 정의한다는 것은 정의하는 클래스가 Sequence 시맨틱을 모두 지원하겠다는 선언을 하는 것이다.** 따라서 이 메소드들을 하나라도 구현하지 않으면 시맨틱이 충족되지 않았다고 파이썬에서 알려주기 때문에 요구되는 시맨틱을 모두 지원하는지 놓치지 않을 수 있다.

Sequence에 요구되는 필수 추상 메소드를 구현하면 별도로 작업하지 않아도 Sequence가 지원하는 index와 count 같은 부가적인 메소드를 자동으로 제공한다.

Set과 MutableMapping처럼 파이썬의 관례에 맞춰 구현해야 하는 특별한 메서드가 많은 더 복잡한 타입을 정의할 때 이런 추상 기반 클래스를 사용하는 이점은 더욱 커진다.


## 4. 핵심정리

* 쓰임새가 간단할 때는 list, dict와 같은 파이썬의 컨테이너 타입에서 직접 상속받게 하자.
* 커스텀 컨테이너 타입을 올바르게 구현하는 데 필요한 많은 메서드에 주의를 기울여야 한다.
* 커스텀 컨테이터 타입이 collections.abc에 정의된 인터페이스 클래스를 상속받게 만들어서 클래스가 필요한 인터페이스, 동작과 일치하게 하자.


# Part 4. 부록. Sequence, Iterable, Iterator
"""
여기서부터는 내가 궁금하기도 했고, 또 알면 유용할 것 같은 위의 세 항목에 대해 하나씩 공부한다.
아마 꼭 도움이 될 것이다.
"""

## 4.1. Sequence

"""
이 책에선 유독 Sequence(이하 시퀀스)라는 단어를 많이 사용했는데,
난 그냥 list류의 클래스를 지칭하는 일반명사라고만 생각했다. 그런데 collections.abc
공식 페이지를 보니 시퀀스는 정의되어 있는 추상클래스이다. 그래서 해당 내용을 번역해보면...

"""


"""Sequence

  An iterable which supports efficient element access using integer indices via the __getitem__() special method and defines a __len__() method that returns the length of the sequence. Some built-in sequence types are list, str, tuple, and bytes. Note that dict also supports __getitem__() and __len__(), but is considered a mapping rather than a sequence because the lookups use arbitrary immutable keys rather than integers.

  The collections.abc.Sequence abstract base class defines a much richer interface that goes beyond just __getitem__() and __len__(), adding count(), index(), __contains__(), and __reversed__(). Types that implement this expanded interface can be registered explicitly using register().

번역 : 
__getitem__을 통해 정수로 인덱싱해서 효율적인 원소 접근을 가능케하는 Iterator.
또한 __len__ 메서드를 정의해서 시퀀스의 길이를 반환해야 한다.

몇몇 내장 시퀀스 타입의 종류는 list, str, tuple, bytes가 있다.
dict 또한 __getitem__와 __len__을 지원하지만, 
정수보다는 일반적으로 불변의 임의의 키를 바탕으로 인덱싱하기 때문에
시퀀스라기 보다는 Mapping으로 간주된다.

collections.abc.Sequence 추상 클래스는 __getitem__과 __len__을 넘어 더 폭넓은 인터페이스를 정의하는데
count, index, __contains__, __reversed__와 같은 메서드가 그 예이다.
( 그래서 str와 list 모두 count 메서드를 쓸 수 있는 것이다.)
이 확장된 인터페이스를 구현하는 타입들은 register라는 메서드를 통해 명시적으로 register(?) 될 수 있다.


이렇게 표현된다. 즉 핵심은, 시퀀스는 __getitem__과 __len__를 가지고
정수 단위로 인덱싱 가능한 이터러블이다. 이터러블은 조금 있다가 살펴본다.

이 클래스를 상속 받으면 나만의 리스트를 또 구현할 수 있을 것 같은데?
혹시 list가 이 Sequence를 상속받은 거 아닌가 해서 찾아봤지만 그건 아니었다.

"""


## 4.2. Iterable

"""
이터러블은 이터레이터, 제너레이터와 함께 친근한 개념이다.
range, filter, map 등을 써봤으면 결과가 보통 우리가 원하는 리스트 형태가 아니라
클래스 object로 나오는 것을 알고 list(   ) 로 감싼 기억이 분명 있을 것이다.
이터러블은 그것과 관련이 있다.

"""

"""Iterable

  An object capable of returning its members one at a time. Examples of iterables include all sequence types (such as list, str, and tuple) and some non-sequence types like dict, file objects, and objects of any classes you define with an __iter__() or __getitem__() method. Iterables can be used in a for loop and in many other places where a sequence is needed (zip(), map(), ...). When an iterable object is passed as an argument to the built-in function iter(), it returns an iterator for the object. This iterator is good for one pass over the set of values. When using iterables, it is usually not necessary to call iter() or deal with iterator objects yourself. The for statement does that automatically for you, creating a temporary unnamed variable to hold the iterator for the duration of the loop. See also iterator, sequence, and generator.


번역 : 

  Iterable(이하 이터러블)은 자신의 멤버를 한 번에 한 개씩 반환가능한 객체를 일컫는다. 
이터러블의 종류는 모든 시퀀스를 포함하고(list, str, tuple) 비-시퀀스(dict, file), 
그 외(__iter__ 메서드를 가진 모든 클래스)도 포함된다.

  이터러블은 for문에서 사용될 수 있고 zip, map과 같이 시퀀스가 필요한 다른 많은 곳에서도 사용된다.
이터러블 객체가 빌트인 함수 iter에 인자로 전달되면, 그 객체의 iterator가 반환된다.
이 iterator는 여러 value 집합에서 인자를 하나씩 전달하기에 좋다.
이터러블을 사용할 때, 일반적으로 직접 iter를 실행하거나, 이터레이터를 실제로 다룰 필요는 없다.
for문이 실제로 직접 그 작업을 수행해주며, 일시적으로 이름 없는 변수를 만들어 그 이터레이터를 저장해서 
for문이 실행되는 동안 사용한다.


  그러니까 이터레이터를 만들 수 있는 객체가 이터러블!
str이 이터러블이라는 사실이 처음에는 혼란스러울 수 있다.
그렇지만 for문에 str을 넣으면 character가 하나씩 뽑아져 나온다는 것을 알면 납득할 수 있는 문제다.

__iter__를 가지고 있어야 하고, 그 결과로 이터레이터를 반환해야 한다.
__next__는 필요 없다.

"""

# example
import random
import string

class MyIterable(list):
    def __init__(self):
	super().__init__()
	for _ in range(100):
	    self.append(random.choice(string.ascii_lowercase))
	
    def __iter__(self): 
	return MyIterator(self)
    # It should return "iterator"

## 4.3. Iterator
"""
Iterator(이하 이터레이터)는 이터러블에서 대충 살펴본 것 같다.
제너레이터와 관련된 내용인데 이참에 둘의 차이점을 제대로 파악하자.
"""

"""Iterator
  An object representing a stream of data. Repeated calls to the iterator’s __next__() method (or passing it to the built-in function next()) return successive items in the stream. When no more data are available a StopIteration exception is raised instead. At this point, the iterator object is exhausted and any further calls to its __next__() method just raise StopIteration again. Iterators are required to have an __iter__() method that returns the iterator object itself so every iterator is also iterable and may be used in most places where other iterables are accepted. One notable exception is code which attempts multiple iteration passes. A container object (such as a list) produces a fresh new iterator each time you pass it to the iter() function or use it in a for loop. Attempting this with an iterator will just return the same exhausted iterator object used in the previous iteration pass, making it appear like an empty container.

More information can be found in Iterator Types.

번역 : 

  데이터의 흐름을 표현하는 객체. 이터레이터의 __next__ 메서드를 계속 실행하면(또는 내장 next 함수에 인자로 전달하면)
이 흐름의 연속되는 아이템을 하나씩 반환한다. 데이터가 더 없다면 StopIteration exception이 대신 발생한다.
이 시점에서, 이터레이터 객체는 모두 소진되어 __next__를 계속 호출해도 StopIteration 에러만 계속된다.
이터레이터는 이터레이터 자신을 반환하는 __iter__ 메서드를 가지고 있어야 하는데,
그렇게 해야 모든 이터레이터가 iterable 해지고 iterable이 필요한 대부분의 경우에서 사용될 수 있다.
한가지 주목할 예외는 다중 iteration passes를 실행하는 코드에서다.(?)
리스트와 같은 container 객체를 iter함수에 전달하거나 for문을 사용하면 신선한 새 이터레이터를 생산한다.
이와 같은 행동을 이터레이터에 시도하면 이전 단계에서 소진된 이터레이터 객체만 나올 뿐이고, 빈 컨테이너처럼 보이기만 할 것이다.


  이터레이터는 __next__ 메소드를 통해 객체를 하나씩 반환하며, 이는 메모리 사용에 도움을 줄 것이다.

__iter__는 자기 자신을 반환하고,
__next__를 꼭 구현해야 한다.
"""

# example

class MyIterator:
    def __init__(self, my_iterable):
	self.iterable = my_iterable
	self.length = len(my_iterable)
	self.count = 0

    def __iter__(self):
	return self

    def __next__(self):
	if self.count < self.length
	    value = self.iterable[self.count] 
	    self.count += 1
	    return value

        else:
	    raise StopIteration



## 4.4. Generator
"""
제너레이터는 이터레이터와 비슷하지만,
조금 다르다. 그 점을 파악하도록 한다.
"""
### 4.4.1 Generator

"""
A function which returns a generator iterator. It looks like a normal function except that it contains yield expressions for producing a series of values usable in a for-loop or that can be retrieved one at a time with the next() function.

Usually refers to a generator function, but may refer to a generator iterator in some contexts. In cases where the intended meaning isn’t clear, using the full terms avoids ambiguity.


번역 : 
  Generator(이하 제너레이터)는 제너레이터 이터레이터를 반환하는 함수이다.
일반 함수처럼 생겼는데 차이점은 제너레이터는 for문이나 next를 써서 value를 연속적으로 반환하는 'yield'식을 포함한다는 것이다.
일반적으로 제너레이터 function을 지칭하지만, 어떤 상황에서는 제너레이터 이터레이터를 가리키기도 한다.
가리키는 의도가 불분명한 상황에서는 전체 용어를 쓰는 것이 좋다.
"""

# example

def gene():
    i = 0
    while i < 10:
        yield i
	i += 1


### 4.4.2. Generator Iterator

"""
An object created by a generator function.

Each yield temporarily suspends processing, remembering the location execution state (including local variables and pending try-statements). When the generator iterator resumes, it picks-up where it left-off (in contrast to functions which start fresh on every invocation).

번역 : 
  제너레이터 함수에 의해 생성되는 객체이다.
각 yield문은 일시적으로 진행을 멈추고, 실행 상태의 위치를 기억한다.(지역변수와 try문까지 포함해서)
제너레이터 이터레이터가 계속되면, 나머지부터 시작하게 된다.(호출할 때마다 새롭게 시작하는 것과 대비된다.
"""

# example

gi = gene()

### 4.4.3. Generator expression

"""
An expression that returns an iterator. It looks like a normal expression followed by a for expression defining a loop variable, range, and an optional if expression. The combined expression generates values for an enclosing function:

번역 :
  이터레이터를 반환하는 표현식이다. 일반 표현식과 비슷한데 루프 변수를 정의하는 for문과 범위 그리고 추가적인 if로 정의된다.

"""

# example

## 1.
gene = (i for i in range(1, 11))

## 2.
sum(i*i for i in range(10)) # 주목! 
