# 119쪽. 공개 속성보다는 비공개 속성을 사용하자.
# 2017/01/05일 작성.

############################################################################


## Part 1.

"""
자바를 해본 사람들이라면 자바에선 클래스의 가시성이
public, default, package, private으로 나뉘는 것을 기억할 것이다.

반면 파이썬에서는 클래스 속성의 가시성이 공개(public)와 비공개(private) 두 유형밖에 없다.

공개는 일반 속성처럼 만들고, 비공개는 속성 이름 앞에 '__'를 붙인다.
"""

class MyObject:
    def __init__(self):
	self.public = 5
	self.__private = 10

    def get_private_field(self):
	return self.__private

    @classmethod
    def get_private_field_of_instance(cls, instance):
	return instance.__private


# 공개 속성은 어디서든 객체에 '.'을 사용해 접근할 수 있다.
foo = MyObject()
assert foo.public == 5


# 비공개 속성은 '.'을 사용해 접근할 수 없다.
assert foo.__private == 10  # AttributeError: 'MyObject' object has no attribute '__private'

# 그렇지만 같은 클래스에 속한 메서드는 비공개 속성에 직접 접근할 수 있다.
assert foo.get_private_field() == 10

# 클래스 메소드도 같은 class 블록에 선언되어 있으므로 비공개 속성에 접근할 수 있다.
assert MyObject.get_private_field_of_instance(foo) == 10



## Part 2.

"""
서브클래스에서 부모 클래스의 비공개 필드에 접근할 수 없다.
"""

class MyParent:
    def __init__(self):
        self.__private_field = 71


class MyChild(MyParent):
    def get_private_field(self):
        return self.__private_field


baz = MyChild()
baz.get_private_field() # AttributeError: 'MyChild' object has no attribute '_MyChild__private_field'



"""
MyChild가 '_MyChild__private_field' 속성이 없다고 출력되는데 이게 무슨 의미일까?
사실 비공개 속성의 동작은 간단하게 속성 이름을 변환하는 방식으로 구현된다.

파이썬은 클래스 정의에서 비공개 필드를 정의하는 코드를 만나면 __private_field를 '_MyChild__private_field'처럼 
'_' + 클래스명 + '__' + 필드명 으로 변환한다. 

실제 이름을 다르게 저장하는 것이다.

또한 파이썬 컴파일러는 MyChild.get_private_field 같은 메서드에서 비공개 속성에 접근하는 코드를 발견하면
아까처럼 __private_field를 '_MyChild__private_field'처럼 바꿔서 찾는다.

필드명을 이렇게 바꿔서 저장하고 검색하니 '__private_field'처럼 
순진하게 접근하면 에러가 뜨는 것이다.

그리고 이 예제에서는 __init__ 메서드 등에서 __private_field를 정의하지 않으므로 baz는 MyChild의 객체임에도
이 필드의 실제 이름은 부모의 비공개 속성 이름인 '_MyParent__private_field'가 된다.

이 체계를 이해하면 접근 권한을 확인하지 않고서도 서브 클래스나 외부 클래스에서 어떤 클래스의 비공개 속성에도
쉽게 접근할 수 있다.
"""

assert = baz._MyParent__private_field == 71

# 객체의 속성 딕셔너리를 들여다보면 실제로 비공개 속성이 변환 후의 이름으로 저장되어 있음을 알 수 있다.

print(baz.__dict__)

# {'_MyParent__private_field': 71}



## Part 3.

"""
이렇게 비공개 속성의 문법이 허술한, 다시 말해 문법을 엄격하게 강제하지 않은 이유가 뭘까?
가장 간단한 답은 파이썬에서 자주 인용되는 "우리 모두 성인이라는 사실에 동의합니다."라는 좌우명에 있다.
파이썬 프로그래머는 개방으로 얻는 장점이 폐쇄로 얻는 단점보다 크다고 믿는다.

그럼에도 무분별하게 객체의 내부에 접근하는 위험을 최소화하기 위햬 파이썬은 관련된 스타일가이드를 가지고 있다.
비공개는 앞에 '__'가 붙는데 '_'를 두 개가 아닌 한 개만 붙여서 '_protected'처럼 보호 필드로 '취급'하는 것이다.
이는 클래스의 외부 사용자들이 신중하게 다뤄야 함을 의미한다.

하지만 파이썬을 처음 접하는 많은 프로그래머들이 서브클래스나 외부에서 접근하면 안 되는 내부 API를 비공개로 나타낸다.
"""

class MyOne:
    def __init__(self, value):
        self.__value = value

    def get_value(self):
        return str(self.__value)

foo = MyClass(5)
assert foo.get_value() == '5'



"""
이 방식은 잘못되었다. 본인을 비롯한 누군가는 클래스에 새 동작을 추가하거나, 기존 메서드의 결함을
해결하려고 서브클래스를 만들기 마련이다. 비공개 속성을 선택하면 서브클래스의 오버라이드과 확장을 다루기 어렵고
불안정하게 만든다. 그리고 아까 확인했듯이 꼭 필요하면 여전히 비공개 필드에 접근할 수도 있고 말이다.
"""

"""
일반적으로 보호 속성을 사용해서 서브클래스가 더 많은 일을 할 수 있게 하는 편이 낫다.
각각의 보호 필드를 문서화해서 서브클래스에서 내부 API 중 어느 것을 쓸 수 있고 어느 것을 그대로 둬야 하는지 설명하자.
이렇게 하면 자신이 작성한 코드를 미래에 안전하게 확장하는 지침이 되는 것처럼 다른 프로그래머에게도 조언이 된다.
"""

class RightOne:
    def __init__(self, value):
        # 사용자가 value를 객체에 전달하는데 이 값은 건드리지 말아야 한다.
        self._value = value


"""
비공개를 사용할지 진지하게 고민할 시점은 서브클래스와 이름이 충돌할 염려가 있을 때뿐이다.
이 문제는 자식 클래스가 부지불식간에 부모 클래스에서 이미 정의한 속성을 정의할 때 일어날 수 있다.
"""

class ApiClass:
    def __init__(self):
        self._value = 5

    def get(self):
        return self._value


class Child(ApiClass):
    def __init__(self):
        super().__init__()
        self._value = 'hello'   # _value가 충돌된다!

a = Child()
print(a.get(), 'and', a._value, 'should be different') # problem..

# >>> hello and hello should be different

"""
주로 클래스가 공개 API의 일부일 때 문제가 된다.
서브클래스는 직접 제어할 수 없으니 문제를 고치려고 리팩토링할 수 없다. 이런 충돌은 속성 이름이 value처럼
아주 일반적일 때 일어날 확률이 특히 높다. 이런 상황이 일어날 위험을 줄이려면 부모 클래스에서 비공개 속성을 사용해서
자식 클래스와 속성 이름이 겹치지 않게 하면 된다.
"""

class ApiClass:
    def __init__(self):
        self.__value = 5

    def get(self):
        return self.__value


class Child(ApiClass):
    def __init__(self):
        super().__init__()
        self._value = 'hello'

b = Child()
print(b.get(), 'and', b._value, 'should be different')

# 5 and hello should be different




"""핵심 정리

* 파이썬 컴파일러는 비공개 속성을 엄격하게 강요하지 않는다.
* 서브클래스가 내부 API와 속성에 접근하지 못하게 막기보다는 처음부터 내부 API와 속성으로
  더 많은 일을 하게 하자.
* 비공개 속성에 대한 접근을 강제로 제어하지 말고, 보호 필드를 문서화해서 서브클래스에서 필요한 지침을 제공하자.
* 직접 제어할 수 없는 서브클래스와 이름이 충돌하지 않게 할 때만 비공개 속성을 사용하는 방안을 고려하자.


"""
