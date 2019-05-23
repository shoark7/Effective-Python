## Better Way 25. super로 부모 클래스를 초기화하자

#### 108쪽

* Created : 2016/12/25
* Modified: 2019/05/23  

<br>

## 1. 파이썬 2의 상속의 단점 1: 생성자 메소드 실행 순서의 어려움

클래스 상속관계를 사용할 때 오래 전 파이썬에서는 자식 클래스에서 부모 클래스의 \_\_init\_\_ 생성자 메소드를 직접 호출하는 방법으로 부모 클래스를 초기화했다.

```python
class MyBaseClass:
    def __init__(self, value):
        self.value = value


class MyChildClass(MyBaseClass):
    def __init__(self):
        MyBaseClass.__init__(self, 5)
```

이 방법은 간단한 계층 구조에서는 잘 작동하지만 많은 경우 제대로 작동하지 않는다. 특히 클래스가 다중 상속(한 서브 클래스가 두 개 이상의 부모 클래스를 상속받는 상속)의 영향을 받는다면 슈퍼클래스의 \_\_init\_\_ 메소드를 직접 호출하는 행위는 예기치 못한 동작을 일으킬 수 있다.  

**초창기 파이썬 2의 클래스 동작의 한 가지 문제점은 다중 상속에서 \_\_init\_\_ 메소드의 호출 순서가 모든 서브 클래스에 걸쳐 명시되지 않았다는 점이다.** 예를 들어 인스턴스의 _value_ 필드로 연산을 수행하는 부모 클래스 두 개를 정의해보자.


```python
class TimesTwo:
    def __init__(self):
        self.value *= 2


class PlusFive:
    def __init__(self):
        self.value += 5
```

다음 클래스는 앞서 정의한 _MyBaseClass_ 와 방금 정의한 두 개의 클래스를 다중 상속받는 클래스를 정의한다. 상속 순서를 눈여겨보기 바란다.

```python
class OneWay(MyBaseClass, TimesTwo, PlusFive):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        TimesTwo.__init__(self)
        PlusFive.__init__(self)
```

_OneWay_ 의 인스턴스를 만들면 _value_ 에 상속 순서와 일치하는 _value_ 값이 정의된다.

```python
foo = OneWay(5)
print("One way's ordering is (5 * 2) + 5 =", foo.value)


One way's ordering is (5 * 2) + 5 = 15
```

5로 초기화한 값에 2를 곱하고 5를 더해 15가 출력됐다. 이는 상속순서와 생성자 메소드 호출순서와 일치한다. 그런데 만약 상속 순서를 다르게 한다면 어떻게 될까?


```python
class AnotherWay(MyBaseClass, PlusFive, TimesTwo):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        TimesTwo.__init__(self)
        PlusFive.__init__(self)
```

새로운 클래스 _AnotherWay_ 를 선언했다. **이 클래스는 생성자 메소드 호출순서는 같지만, 상속순서를 다르게 해서 _value_ 에 5를 더하는 클래스를 먼저 상속받는다.**

```python
bar = AnotherWay(5)
print("Second way's result is still", bar.value)


Second way's result is still 15
```

결과값은 여전히 15이다. 그러니까 결론은 **다중상속관계에서 생성자 호출 순서는 상속받는 순서와 상관없이 생성자 직접 호출 순서에 의해 결정된다는 것이다.** 이는 뭔과 직관적이지 않다. 이는 단순히 헷갈리는 문제이고 익숙해지면 괜찮다고 생각할 수도 있지만 더 큰 문제가 기다리고 있다.

<br>


## 2. 파이썬 2의 상속의 단점 2: 슈퍼클래스 생성자 함수의 중복 실행

다른 문제는 `다이아몬스 상속(diamond inheritance)`에서 찾을 수 있다. 다이아몬드 상속은 서브 클래스가 계층 구조에서 같은 슈퍼클래스를 둔 서로 다른 두 클래스를 상속받을 때 발생한다.

![Diamond inheritance example](../images/diamond-inheritance.png)

**다이아몬스 상속은 공통 슈퍼클래스의 \_\_init\_\_ 메소드를 여러 번 실행하게 해서 예상치 못한 동작을 일으킨다.** 예를 들어, _MyBaseClass_ 에서 상속받는 자식 클래스 두 개를 정의하자.

```python
class TimesFive(MyBaseClass):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        self.value *= 5


class PlusTwo(MyBaseClass):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        self.value += 2
```

이 클래스는 _value_ 에 5를 할당하는 _MyBaseClass_ 를 공통 상속하고 있다. 다음으로 두 클래스를 모두에서 상속받는 자식 클래스를 정의하여 _MyBaseClass_ 를 다이아몬드의 꼭대기로 만든다.

```python
class ThirdWay(TimesFive, PlusTwo):
    def __init__(self, value):
        TimesFive.__init__(self, value)
        PlusTwo.__init__(self, value)
```

예제를 만들어보자.


```python
foo = ThirdWay(5)
print("Result should be (8 * 5) + 2 = 27, but it's", foo.value)


Result should be (5 * 5) + 2 = 27, but it's 7 
```

예상대로라면 초기화된 5에 5를 곱하고 2를 더해서 27이 나오리라고 예상할 수 있지만 7이라는 쌩뚱맞은 값이 나왔다. 왜 그럴까? 그 이유는 생각보다 싱겁다. 첫 번째 부모 클래스의 생성자가 호출되어 _MyBaseClass_ 가 한 번 실행된뒤, **두 번째 부모 클래스의 생성자 *PlusTwo.\_\_init\_\_* 를 호출하는 코드에서 *MyBaseClass.\_\_init\_\_* 가 두 번째 호출될 때 _self.value_ 가 5로 다시 리셋되기 때문이다.**

보통 이런 상황에서 공통 슈퍼클래스의 생성자 함수가 두 번 실행되는 것을 기대하지는 않는다. 


<br>

## 3. 해결책: super 내장함수 사용

까마득한 예전에 **파이썬 2.2 부터는 위와 같은 문제들을 해결하기 위해 _super_ 내장함수를 추가하고 메소드 해석 순서(MRO, Method Resolution Order)를 정의했다. MRO는 다중 상속에서 상속 순서에 따라 어떤 슈퍼클래스부터 초기화하는지를 정한다. 그 순서는 '깊이 우선, 왼쪽에서 오른쪽으로'가 기본 원칙이다. 결정적으로 다이아몬드 계층 구조에 있는 공통 슈퍼클래스를 단 한 번만 실행하게 한다.**

다음 코드는 다이아몬드 클래스 구조지만 _super_ 로 부모 클래스를 초기화한다. 먼저 파이썬 2의 버전부터 살펴본다.

```python
# 파이썬 2방식
class TimesFiveCorrect(MyBaseClass):
    def __init__(self, value):
        super(TimesFiveCorrect, self).__init__(value)
        self.value *= 5


class PlusTwoCorrect(MyBaseClass):
    def __init__(self, value):
        super(PlusTwoCorrect, self).__init__(value)
        self.value += 2
```

이 둘을 상속받는 클래스를 정의한다. 상속 순서를 눈여겨 보길 바란다.

```python
class GoodWay(TimesFiveCorrect, PlusTwoCorrect):
    def __init__(self, value):
        super(GoodWay, self).__init__(value)


foo = GoodWay(5)
print('Should be 5 * (5 + 2) = 35 and the result is', foo.value)


Should be 5 * (5 + 2) = 35 and the result is 35
```


이 결과를 어떻게 이해해야 할까? 상술했듯이 바뀐 파이썬의 상속 정책, MRO에서는 초기화 순서가 '깊이 우선, 왼쪽에서 오른쪽으로' 방식으로 진행된다.  **MRO의 동작 방식은 본질적으로 Stack과 유사하다. _GoodWay_ 부터 시작해서 상속받는 클래스의 왼쪽부터 스택에 집어넣는다. 이후 모든 클래스의 조상 _object_ 클래스까지 도달하면 스택에서 한 클래스씩 빼내서 클래스 생성자를 실행한다.** 그랬기 때문에 5를 먼저 초기화했고(_MyBaseClass_), 그 값에 2를 더했으며(_PluseTwoCorrect_), 5를 곱해(_TimesFiveCorrect_) 35라는 5와 7의 최소공배수가 나올 수 있었다.

또한 정확한 MRO 순서는 _mro_ 라는 클래스 메소드로 확인할 수 있다.

```python
from pprint import pprint

pprint(GoodWay.mro())


[<class '__main__.GoodWay'>,
 <class '__main__.TimesFiveCorrect'>,
 <class '__main__.PlusTwoCorrect'>,
 <class '__main__.MyBaseClass'>,
 <class 'object'>]
```


<Br>

## 4. 파이썬 3에서의 super의 개선

앞서 파이썬 2.2에서 추가된 _super_ 함수의 사용법을 다시 살펴보자.

```python
super(GoodWay, self).__init__(value)
```

이 함수는 끝내주게 잘 동작하지만 두 가지 문제점이 있다.

* **문법이 장황하다.**
  - 현재는 함수를 호출할 때 정의하는 클래스, sef, \_\_init\_\_ 과 모든 인수를 설정해야 한다. 언제나 상태가 많아지면 복잡해지고 가독성이 떨어지기 마련이다.
* **_super_ 를 호출하면서 현재 클래스의 이름을 지정해야 한다.**
  - 클래스의 이름을 변경하는 일은 클래스 계층 구조를 개선할 때 아주 흔히 하는 행동이다. 이때 _super_ 를 호출하는 모든 코드를 수정해야 하는 번거로움이 있다.

<br>

파이썬에서는 _super_ 의 문제점을 개선했다. 파이썬 3에서는 _super_ 를 인수 없이 호출하면 *\_\_class\_\_* 와 _self_ 를 인수로 넘겨서 호출한 것으로(default 값으로 설정해서) 처리해서 이 문제를 해결한다. 파이썬 3에서는 항상 _super_ 를 사용해야 한다. 이 내장함수는 명확하고 간결하며 항상 제대로 동작한다.


```python
class ExplicitOne(MyBaseClass):
    def __init__(self, value):
        super(__class__, self).__init__(value * 2)


class ImplicitOne(MyBaseClass):
    def __init__(self, value):
        super().__init__(value * 2)


assert ExplicitOne(10).value == ImplicitOne(10).value


```

<Br>

## 5. 핵심 정리

* 파이썬의 표준 메소드 해석 순서(MRO)는 슈퍼클래스의 초기화 순서와 다이아몬드 상속 문제를 해결한다.
* 항상 내장함수 _super_ 로 부모 클래스를 초기화하자.
