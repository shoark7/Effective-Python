# 134쪽. 게터와 세터 메서드 대신에 일반 속성을 사용하자.
# 2017년 1월 10일 작성.

"""
자바 수업을 듣던 때가 생각난다. 자바에서는 클래스의 속성에 접근하고 설정하는
getter(이하 게터), setter(이하 세터) 메서드를 작성하는데,
자바의 대표적인 IDE 이클립스에서는 게터와 세터 메서드를 자동 완성하는 기능까지 지원한다.

그래서 자바를 공부한 사람들은 파이썬에서도 게터와 세터를 지정하고는 하는데
이는 별로 좋은 습관이 아니다.
"""


#### Part 1. 파이썬은 게터, 세터가 필요 없다.

class OldWay:
    def __init__(self, ohms):
        self._ohms = ohms

    def get_ohms(self):
        return self._ohms

    def set_ohms(self, ohms):
        self._ohms = ohms

r0 = OldWay(30)
assert r0.get_ohms() == 30
r0.set_ohms(10)
assert r0.get_ohms() == 10


# 특히 게터와 세터는 즉석에서 값을 증가시키는 연산에는 사용하기 불편하다.
r0.set_ohms(r0.get_ohms() + 5)


"""
이런 유틸리티 메서드는 클래스의 인터페이스를 정의하는 데 도움이 되고, 
기능을 캡슐화하고 사용법을 검증하고 경계를 정의하기 쉽게 해준다.
이런 요소는 클래스가 시간이 지나면서 발전하더라도 호출하는 쪽 코드를 절대
망가뜨리지 않도록 설계할 때 중요한 목표가 된다.
"""

"""
하지만 파이썬에서는 이런 게터, 세터를 굳이 만들 이유가 없다.
대신 항상 간단한 공개 속성부터 구현하기 시작해야 한다.
"""


class Register:
    def __init__(self, ohms):
        self.ohms = ohms
        self.voltage = 0
        self.current = 0

r1 = Register(400)
r1.ohms = 10e3

# 이렇게 하면 즉석에서 값 증가시키기 같은 연산이 자연스럽고 명확해진다.
r1.ohms += 1e3



#### Part 2. 특별한 동작이 필요하면 @property를 쓰면 된다.
"""
그런데 파이썬에서도 자바처럼 게터와 세터의 대체가 필요한 경우가 생길 수 있다.

나중에 속성을 설정할 때 특별한 동작이 일어나야 한다면, @property 데코레이터와
이에 해당하는 setter 속성을 사용하는 방법으로 바꿀 수 있다.

여기서는 Register의 서브클래스를 정의하며 voltage 프로퍼티를 할당하면 
current 값이 바뀌게 해본다.

제대로 동작하려면 세터와 게터 메서드의 이름이 의도한 프로퍼티 이름과 일치해야 한다.
"""

class VoltageRegister(Register):
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

"""
@property가 뭔지 살펴보자. '@'는 데코레이터의 의미로서 나중에 더 살펴본다.
@property를 쓰면 voltage라는 메소드에 '속성'처럼 접근할 수 있다.

즉 'voltage_instance.volatage' 처럼 쓸 수 있는 것이다.

두 번째로 voltage.setter는 말 그대로 세터처럼 값을 설정할 수 있다.
'voltage_instance.voltage = 3'처럼 입력하면 
  1. _voltage값이 3으로 설정되고
  2. current라는 값이 그에 맞춰 설정되는 것이다.
"""

r2 = VoltageRegister(100)
assert r2.voltage == 0
r2.voltage = 500
assert r2.voltage == 500
# voltage가 속성인데도 불구하고 메서드처럼 접근하고 있다.


"""
프로퍼티에 setter를 설정하면 클래스에 전달된 값들의 타입을 체크하고
값을 검증할 수 있다. 다음은 모든 저항값이 0 옴보다 큼을 보장하는 클래스를 정의한 것이다.
"""

class BoundedRegistance(Register):
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


"""
지금껏 난 특정한 하나의 값을 검증할 때 __init__과 다른 메서드들에서
여러 번 검증식을 써야 했다. 하지만 이렇게 하면...
"""

r3 = BoundedRegistance(1e3)
# r3.ohms = 0
# >>> ValueError: Ohms must be over 0.

# r4 = BoundedRegistance(-5)
# >>> ValueError: Ohms must be over 0.

"""
뭔지 알겠는가? __init__에 검증식을 넣지 않았는데도 인스턴스를 생성할 때
검증이 되는 것이다. 왜냐하면 __init__에 ohms를 설정하는 문장이 있고,(self.ohms = ..)
그래서 setter가 발동되는 것!
"""



"""
또한 부모 클래스의 속성을 불변으로 만드는 데도 @property를 사용할 수 있다.
"""

class FixedRegistance(Register):
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
# r4.ohms = 2e3
# >>> AttributeError: Can't set attribute

# ohms 값이 이미 설정되어 있기 때문에 설정할 수 없다. Singleton!


#### Part3. @property의 단점.

"""
@property의 가장 큰 단점은 속성에 대응하는 메서드를 서브클래스에서만 
공유할 수 있다는 점이다.
서로 관련이 없는 클래스는 같은 구현을 공유하지 못한다.

하지만 파이썬은 재사용 가능한 프로퍼티 로직을 비롯해 다른 많은 쓰임새를
가능하게 하는 디스크립터(descriptor)도 지원한다. 31장에서 배운다.

마지막으로 @property 메서드로 게터와 세터를 구현할 때 예상과 다르게
동작하지 않게 해야 한다. 예를 들면 게터 프로퍼티 메서드에서 다른 속성을
설정하지 말아야 한다.
"""

class MysteriousRegister(Register):
    def __init__(self, ohms):
        self._ohms = ohms
        self.voltage = 0

    @property
    def ohms(self):
        self.voltage = self._ohms * self.current
        return self._ohms


# 이와 같은 코드는 아주 이상한 동작을 만들어낸다.

r7 = MysteriousRegister(10)
r7.current = 0.01
assert r7.voltage == 0
r7.ohms
assert r7.voltage == 0.1

"""
이 코드의 문제점은 우리는 분명 ohms을 건드렸는데 쌩뚱맞게
voltage 속성값이 변화를 겪었다는 점이다. 일반적으로 게터와 세터를 쓰는
유저는 이런 일반적이지 않고, 예측하기 힘든 결과를 바라지 않을 것이다.

이런 경우와 더불어 게터와 세터에서
  1. 모듈을 동적으로 import하거나(__import__, importlib.import_module),
  2. 느린 헬퍼 함수를 실행하거나,
  3. 비용이 많이 드는 데이터베이스 쿼리를 수행하는 일

처럼 일반적으로 예상하지 않는 부작용을 유발할 수 있는 동작은 피해야 한다.

파이썬 사용자는 다른 언어와 마찬가지로 클래스 속성이 빠르고 쉬울 것이라고 예상할 것이다. 더 복잡하거나 느린 작업은 일반 메서드로 하자.
"""



"""핵심 정리

* 간단한 공개 속성을 사용하여 인스턴스를 정의하고 게터와 세터 메서드는 사용하지 말자.
* 객체의 속성에 접근할 때 특별한 동작을 정의하려면 @property를 사용하자.
* @property 메서드에서 최소 놀람 규칙(rule of least surprise)를 따르고 이상한 부작용은 피하자.
* @property 메서드가 빠르게 동작하도록 만들자. 느리거나 복잡한 작업은 일반 메서드로 하자.

"""
