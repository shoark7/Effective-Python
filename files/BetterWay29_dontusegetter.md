## Better Way 29. 게터와 세터 메소드 대신에 일반 속성을 사용하자

#### 134쪽

* Created : 2017/01/10
* Modified: 2019/05/30 

<br>

## 1. 타 언어의 getter와 setter


자바 수업을 듣던 때가 생각난다. 자바에서는 클래스의 속성에 접근하고 설정하는 getter(이하 '게터'), setter(이하 '세터') 메소드를 작성하는데, 자바의 대표적인 IDE 이클립스에서는 게터와 세터 메소드를 자동 완성하는 기능까지 지원한다.

그래서 자바 등의 타 언어를 공부한 사람들은 파이썬에서 클래스를 정의할 때도 흔히 게터와 세터를 지정하고는 한다.

```python
class OldWay:
    def __init__(self, ohms):
        # 'ohms'는 전기저항의 단위로서 'Ω' 기호를 사용함. 기억나지? ㅋㅋ
        self._ohms = ohms

    def get_ohms(self):
        return self._ohms

    def set_ohms(self, ohms):
        self._ohms = ohms


r0 = OldWay(30)
assert r0.get_ohms() == 30
r0.set_ohms(10)
assert r0.get_ohms() == 10
```

타 언어 사용자들에게는 익숙할 수 있지만 Pythonic 하지는 않다. 게터와 세터 메소드는 즉석에서 값 변화시키기 같은 연산에서 사용하기 불편하다.

```python
r0.set_ohms(r0.get_ohms() + 5)
```

옴 값을 단순히 5 증가시키려는데 함수 호출이 두 번이나 필요하다.

<br>

객체의 속성에 접근하는 이와 같은 유틸리티 메소드는 클래스의 인터페이스를 정의하는 데 도움이 되고, 기능을 캡슐화하고 사용법을 검증하고 경계를 정의하기 쉽게 해준다.

**이런 요소는 클래스가 시간이 지나면서 발전하더라도 호출하는 쪽 코드를 절대 망가뜨리지 않도록 설계할 때부터 중요한 목표가 된다.** 즉 설계할 때부터 확장성을 고려해야 한다는 것과도 대응된다.

하지만 **파이썬에서는 이런 게터, 세터를 굳이 만들 이유가 없다.** 대신 항상 간단한 공개 속성부터 구현하기 시작해야 한다.


```python
class Registor:
    def __init__(self, ohms):
        self.ohms = ohms
        self.voltage = 0
        self.current = 0

r1 = Registor(400)
r1.ohms = 10e3

# 이렇게 하면 즉석에서 값 증가시키기 같은 연산이 자연스럽고 명확해진다.
r1.ohms += 1e3
```

<br>

## 2. 파이썬의 게터와 세터: @property와 .setter

그런데 파이썬에서도 자바처럼 게터와 세터의 대체가 필요한 경우가 생길 수 있다. **나중에 속성을 설정할 때 특별한 동작이 추가로 일어나야 한다면, @property 데코레이터와 이에 해당하는 setter 속성을 사용하는 방법으로 바꿀 수 있다.**

여기서는 앞서 정의한 _Registor_ 의 서브클래스를 정의하며 voltage(전압) 프로퍼티를 할당하면 current(현재 전류) 값이 바뀌게 해본다.

**제대로 동작하려면 세터와 게터 메소드의 이름이 의도한 프로퍼티 이름과 일치해야 한다.**

```python
class VoltageRegistor(Registor):
    def __init__(self, ohms):
        super().__init__(ohms)
        self._voltage = 0

    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, voltage):
        self._voltage = voltage
        self.current = self._voltage / self.ohms
	# 전류는 '전압 / 저항'과 같다고 합니다...
```

@property가 뭔지 살펴보자. '@'는 데코레이터의 의미로서 나중에 더 살펴본다. **@property를 쓰면 voltage라는 메소드에 '속성'처럼 접근하고 평가값을 구할 수 있다.** 즉 'object.volatage' 처럼 속성처럼 호출하고 그 값을 받아올 수 있다.

두 번째로 **_@voltage.setter_ 는 말 그대로 세터처럼 값을 설정하는 것에 더해 근본적으로 함수이기 때문에 추가적인 동작을 넣을 수 있다.** 'object.voltage = 3'처럼 입력하면 

1. _\_voltage_ 값이 3으로 설정되고
1. _current_ 라는 전류 값이 그에 맞춰 설정된다.


```python
r2 = VoltageRegistor(100)
assert r2.voltage == 0
r2.voltage = 500
assert r2.voltage == 500

# voltage가 메소드임에도 속성이나 변수처럼 접근하고 있다.
```

<br>

다음으로 **_@property_ 에 대응되는  _setter_ 를 설정하면 클래스에 전달된 값들의 타입을 체크하고 값을 검증할 수 있다.** 다음은 모든 저항값이 0 옴보다 큼을 보장하는 클래스를 정의한 것이다.

```python
class BoundedRegistance(Registor):
    def __init__(self, ohms):
        super().__init__(ohms)

    @property
    def ohms(self):
        return self._ohms

    @ohms.setter
    def ohms(self, ohms):
        if ohms <= 0:
            raise ValueError("Ohms must be over 0.")
        self._ohms = ohms
```

지금껏 난 특정한 하나의 값을 검증할 때 __init__과 다른 메소드들에서
여러 번 검증식을 써야 했다. 하지만 이렇게 하면...

```python
r3 = BoundedRegistance(1e3)


r3.ohms = 0
ValueError: Ohms must be over 0.

r4 = BoundedRegistance(-5)
ValueError: Ohms must be over 0.
```

옴이 0 이하인 경우에는 _ValueError_ 를 반환한다. 그런데 신기하게도 **_r4_ 처럼 @setter가 아닌 생성자에 음의 옴 값을 넣어줘도 에러가 발생한다.** 분명 저항 검증식은 인스턴스 생성자가 아닌 _ohms_ 세터 메소드에 넣었는데 말이다. 이게 참 재미있는 일이다. **생성자를 호출하면 부모클래스인 _Registor_ 의 생성자가 호출된다. 이때 _ohms_ 가 전달되는데 생성자 코드 안에 옴을 할당하는 식이 있고, 이 할당식이 자식클래스의 ohms 세터 메소드를 호출한다.**


<br>

또한 **부모클래스의 속성을 불변으로 만드는 데도 @property를 사용할 수 있다.**

```python
class FixedRegistance(Registor):
    def __init__(self, ohms):
        super().__init__(ohms)

    @property
    def ohms(self):
        return self._ohms

    @ohms.setter
    def ohms(self, ohms):
        if hasattr(self, 'ohms'):
             raise AttributeError("Can't set attribute")
        self._ohms = ohms

r4 = FixedRegistance(1000)
r4.ohms = 2e3


AttributeError: Can't set attribute
```

_FixedRegistance_ 클래스에서는 생성자에서 _ohms_ 를 할당한다. 그리고 다음 할당이 있을 때마다 객체는 _ohms_ 속성을 갖고 있기 때문에 전부 _AttributeError_ 를 반환하게 된다. 즉 **세터를 통해 속성 싱글턴(Singleton) 디자인 패턴을 구현한 것이다.**


<br>

## 3. @property의 단점.

**@property의 가장 큰 단점은 속성에 대응하는 메소드를 서브클래스에서만 공유할 수 있다는 점이다.** 서로 관련이 없는 클래스는 같은 구현을 공유하지 못한다.

**하지만 파이썬은 재사용 가능한 프로퍼티 로직을 비롯해 다른 많은 쓰임새를 가능하게 하는 디스크립터(descriptor)도 지원한다. 31장에서 배운다.**

마지막으로 **@property 메소드로 게터와 세터를 구현할 때 지나치게 복잡하거나 예상과 다르게 동작하지 않게 해야 한다.** 예를 들면 게터 프로퍼티 메소드에서 다른 속성을 설정하지 말아야 한다.

```python
class MysteriousRegistor(Registor):
    def __init__(self, ohms):
        self._ohms = ohms
        self.voltage = 0

    @property
    def ohms(self):
        self.voltage = self._ohms * self.current
        return self._ohms
```

이와 같은 코드는 아주 이상한 동작을 만들어낸다.

```python
r7 = MysteriousRegistor(10)
r7.current = 0.01
assert r7.voltage == 0
r7.ohms
assert r7.voltage == 0.1
```

이 코드의 문제점은 우리는 분명 ohms을 건드렸는데 쌩뚱맞게 voltage 속성값이 변화를 겪었다는 점이다. 일반적으로 게터와 세터를 쓰는 유저는 이런 일반적이지 않고, 예측하기 힘든 결과를 바라지 않는다.

이런 경우와 더불어 게터와 세터에서

1. 모듈을 동적으로 import하거나(\_\_import\_\_, importlib.import\_module),
1. 느린 헬퍼 함수를 실행하거나,
1. 비용이 많이 드는 데이터베이스 쿼리를 수행하는 일

처럼 일반적으로 예상하지 않은 복잡하거나 부작용을 유발할 수 있는 동작은 피해야 한다.

**파이썬 사용자는 다른 언어와 마찬가지로 클래스 속성이 빠르고 쉬울 것이라고 예상할 것이다. 더 복잡하거나 느린 작업은 일반 메소드로 하자.**


<br>

## 4. 핵심 정리

* 간단한 공개 속성을 사용하여 인스턴스를 정의하고 타 언어의 게터와 세터 메소드는 사용하지 말자.
* 객체의 속성에 접근할 때 특별한 동작을 정의하려면 @property를 사용하자.
* @property 메소드에서 최소 놀람 규칙(rule of least surprise)를 따르고 이상한 부작용은 피하자.
* @property 메소드가 빠르게 동작하도록 만들자. 느리거나 복잡한 작업은 일반 메소드로 하자.
