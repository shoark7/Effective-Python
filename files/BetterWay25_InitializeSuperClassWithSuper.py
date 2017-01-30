# 108쪽 super로 부모 클래스를 초기화하자.
# 2016/12/25일 작성.

############################################################################

"""
이전에는 자식 클래스에서 부모 클래스의 __init__ 메서드를 직접 호출하는
방법으로 부모 클래스를 초기화했다.
"""


class MyBaseClass(object):
    def __init__(self, value):
        self.value = value


class MyChildClass(MyBaseClass):
    def __init__(self):
        MyBaseClass.__init__(self, 5)


"""
이 방법은 간단한 계층 구조에서는 잘 먹힌다. 하지만 바람직하지 않다.
클래스가 다중 상속을 받는다면 슈퍼클래스의 __init__ 메소드를 직접 호출하는 행위는
예기치 못한 동작을 일으킬 수 있다.

한 가지 문제는 __init__의 호출 순서가 모든 서브 클래스에 걸쳐 명시되어 있지 않다는 점이다.
예를 들어보자.
"""


class TimesTwo(object):
    def __init__(self):
        self.value *= 2


class PlusFive(object):
    def __init__(self):
        self.value += 5


class OneWay(MyBaseClass, TimesTwo, PlusFive):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        TimesTwo.__init__(self)
        PlusFive.__init__(self)


"""
이 클래스의 인스턴스를 생성해서 value의 값을 예상해보자.
원래 값 5에 2를 곱하고 5를 더하니 아마 15가 나올 것 같다.

"""

foo = OneWay(5)
print('First ordering of OneWay is (5 * 2) + 5 =', foo.value)

"""
예상대로 15가 나올 것이다. 하지만, 만약 __init__메서드에서 TimesTwo와 PlusFIve의
상속 순서는 그대로 두고, 실행순서를 다르게 하면 어떨까?
"""


class AnotherWay(MyBaseClass, PlusFive, TimesTwo):

    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        TimesTwo.__init__(self)
        PlusFive.__init__(self)


foo = AnotherWay(5)
print('Second ordering of AnotherWay is still', foo.value)

"""
즉메소드들의 실행 순서는 상속순서와 상관없이, __init__메서드의 실행순서에
의해 결정된다는 것이다. 상속 순서에서 일관된 순서가 필요없어진 것으로 바람직하지 않다.
"""

"""
다른 문제는 다이아몬드 상속이다. 다이아몬드 상속(diamond inheritance)란 서브 클래스가 계층
구조에서
같은 슈퍼클래스를 둔 서로 다른 두 클래스에서 상속받을 때 발생한다.
다이아몬드 상속은 공통 슈퍼클래스의 __init__ 메서드를 여러 분 실행하게 되어 예상치 못한 동작을
일으킨다. 예를 보자.
"""


class TimesFive(MyBaseClass):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        self.value *= 5


class PlusTwo(MyBaseClass):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        self.value += 2


# 두 클래스가 모두 MyBaseClass의 __init__메소드를 실행하고 있다.
# 이제 이 둘을 모두 상속받는 서브 클래스를 만들어 보자.
# 과연 메소드가 두 번 실행될까?


class ThisWay(TimesFive, PlusTwo):
    def __init__(self, value):
        TimesFive.__init__(self, value)
        PlusTwo.__init__(self, value)


foo = ThisWay(5)
print('Should be (5 * 5) + 2 = 27, but ThisWay is', foo.value)

"""
충격적이게도 결과는 7이 나온다. 왜 그럴까?
이유는 다음과 같다.

MyBaseClass의 __init__이 두 번 실행되면서 두 번째 __init__이 실행될때,
value를 5로 다시 reset해버린다. 그렇기 때문에 5 + 2가 되어 7이 나오게 된다.

파이썬에서는 이 문제를 해결하기 위해 super라는 내장 함수가 있다.
또한 MRO(Method Resolution Order)를 정의했는데 이는 어떤 슈퍼클래스부터
초기화할지를 정한다.(깊이 우선, 왼쪽에서 오른쪽으로)

또한 다이아몬드 계층 구조에 있는 공통 슈퍼클래스를 단 한번만 실행하게 한다.
"""


# Python 2 way
class TimesFiveCorrect(MyBaseClass):
    def __init__(self, value):
        super(TimesFiveCorrect, self).__init__(value)
        self.value *= 5


class PlusTwoCorrect(MyBaseClass):
    def __init__(self, value):
        super(PlusTwoCorrect, self).__init__(value)
        self.value += 2


# 이제 다이아몬드의 꼭대기인 MyBaseClass.__init__가 한 번만 실행된다.
# 다른 부모 클래스는 class문으로 지정한 순서대로 실행된다.

class GoodWay(TimesFiveCorrect, PlusTwoCorrect):
    def __init__(self, value):
        super(GoodWay, self).__init__(value)


foo = GoodWay(5)
print('sholud be 5 * (5 + 2) of GoodWay is 35, and is', foo.value)


"""
답은 35가 나온다. 연산이 뒤에서부터 실행되는 것 같은데 이상하지 않은가?
5 * 5 + 2 = 27이 나오게 할 수는 없는가? 답은 '없다'이다.

이 순서는 이 클래스에 대해 MRO가 정의하는 순서와 일치한다.
MRO는 mro라는 클래스 메서드로 알 수 있다.

GoodWay를 호출하면 먼저 TimesFiveCorrect.__init__가 실행되고,
이는 PlusFiveCorrect를 호출한다. 이런 호출이 다이아몬드의 꼭대기에 도달하면
모든 초기화 메서드는 역순으로 실행된다.
"""

"""
이 방법의 문제는 무엇일까? 일단 문법이 장황하다. super함수 내에 필요 이상으로
글자가 많이 들어간다. 그래서 파이썬을 처음 접하는 사람들에게는 스트레스를 줄 수 있다.

두 번째는 super를 호출하면서 현재 클래스의 이름을 지정해야 한다는 것이다.
리팩토링을 통해 클래스 이름이 변하는 경우가 다반사인데, 이때마다
super 코드도 같이 수정해줘야 한다.

그래서 파이썬 3에서는 기존 방법과 함께 super를 인자 없이 쓸 수 있도록 하고 있다.
파이썬 3에서는 super이 간결하고 명확하기 때문에 항상 써주는 것이 좋다.

"""


class Explicit(MyBaseClass):
    def __init__(self, value):
        super(__class__, self).__init__(value * 2)


class Implicit(MyBaseClass):
    def __init__(self, value):
        super().__init__(value * 2)


assert Explicit(10).value == Implicit(10).value


"""
결론 :
    1. 파이썬의 MRO는 슈퍼 클래스의 초기화 순서와 다이아몬드 상속을 해결한다.
    2. 항상 내장함수 super로 부모 클래스를 초기화하자!
"""
