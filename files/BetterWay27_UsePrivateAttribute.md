## Better Way 27. 공개 속성보다는 비공개 속성을 사용하자

#### 119쪽

* Created : 2017/01/05
* Modified: 2019/05/27  

<br>


## 1. 파이썬 클래스에서의 비공개 속성


자바를 해본 사람들이라면 자바에서 클래스의 가시성이 'public', 'default', 'package', 'private'와 같이 나뉘는 것을 기억할 것이다. 반면 **파이썬에서는 클래스 속성의 가시성이 공개(public)와 비공개(private) 두 유형밖에 없다.**

공개는 일반 변수처럼 이름 짓고, **비공개 속성은 이름 앞에 `__`를 붙인다.**


```python
class MyObject:
    def __init__(self):
        self.public = 5
        self.__private = 10

    def get_private_field(self):
        return self.__private

    @classmethod
    def get_private_field_of_instance(cls, instance):
        return instance.__private
```


공개 속성은 어디서든 객체에 '.'을 사용해 접근할 수 있다.

```python
foo = MyObject()
assert foo.public == 5
```

반면 비공개 속성은 클래스 외부에서 '.'을 사용해 직접 접근하면 예외가 일어난다.

```python
assert foo.__private == 10  # AttributeError: 'MyObject' object has no attribute '__private'
```

그렇지만 같은 클래스에 속한 메서드는 비공개 속성에 직접 접근할 수 있다.

```python
assert foo.get_private_field() == 10
```

클래스 메소드도 같은 class 블록에 선언되어 있으므로 비공개 속성에 접근할 수 있다.

```python
assert MyObject.get_private_field_of_instance(foo) == 10
```

또한 비공개 필드의 주요한 특징으로 **서브클래스에서는 부모클래스의 비공개 필드에 직접 접근할 수 없다.**

```python
class MyParent:
    def __init__(self):
        self.__private_field = 71

class MyChild(MyParent):
    def get_private_field(self):
        return self.__private_field


baz = MyChild()
baz.get_private_field()

AttributeError: 'MyChild' object has no attribute '_MyChild__private_field'
```

이 이유는 비공개 속성의 동작의 독특한 방식 때문인데, 클래스에 비공개 속성을 할당하면 외부에 변수를 노출시키지 않는 대단한 로직이 있는 것이 아니라 단순히 속성 이름을 변환하는 방식으로 구현된다. 

파이썬 컴파일러는 _MyChild.get\_private\_field_ 같은 메소드에서 비공개 속성에 접근하는 코드를 발견하면 *\_\_private\_field*를 _MyChild\_\_private\_field_ 에 접근하는 코드로 변환한다. 이 예제에서는 *\_\_private\_field* 가 *MyParent.\_\_init\_\_* 에만 정의되어 있으므로 비공개 속성의 실제 이름은 _MyParent\_\_private\_field_ 가 된다. 자식클래스에서 부모의 비공개 속성에 접근하는 동작은 단순히 변환된 속성 이름이 일치하지 않아서 실패하는 것이다.

이 체계를 이해하면 공개, 비공개 등 접근 권한을 확인하지 않고서도 서브클래스나 외부 클래스에서 어떤 클래스의 비공개 속성이든 쉽게 접근할 수 있다.

```python
assert baz._MyParent__private_field == 71
```

_baz_ 는 자식 클래스(_MyChild_)의 인스턴스임에도 부모 클래스에서 정의한 비공개 클래스에 접근할 수 있게 되었다. 추가로 객체의 속성 딕셔너리를 들여다보면 실제로 비공개 속성이 변환 후의 이름으로 저장되어 있음을 알 수 있다.



```python
print(baz.__dict__)

{'_MyParent__private_field': 71}
```

**왜 파이썬에서는 다른 고급 언어들과 달리 가시성을 엄격하게 강제하지 않을까? 가장 간단한 답은 파이썬에서 자주 인용되는 "우리 모두 성인이라는 사실에 동의합니다"라는 좌우명에 있다.** 파이썬 프로그래머들은 개방으로 얻는 장점이 폐쇄로 얻는 단점보다 크다고 믿는다.  

파이썬의 이런 특징은 이외에도 속성에 접근하는 것처럼 언어 기능을 가로채는 기능을 사용해 마음만 먹으면 언제든지 객체의 내부를 조작할 수 있다. 우리가 이전 장에서 _setattr_ 함수로 객체에 속성을 동적으로 할당한 것을 예로 들 수 있겠다.


<br>

## 2. 비공개 속성 사용의 문제점

그러면 완전히 다른 질문으로 '이럴거면 애초에 엉성한 비공개 속성 자체를 두는 이유가 있냐고 할 수 있냐'고 물을 수 있다. 충분히 합리적인 질문으로 비공개 속성을 두기라도 두는 것이 어떤 가치가 있을까?

과유불급이라고, 무분별하게 객체의 내부에 접근하는 것에도 위험이 따른다. 파이썬 프로그래머들은 이 위험을 최소화하기 위해 스타일가이드에 정의된 명명 관례를 따른다. **\_protected\_field 처럼 앞에 `_`를 한 개 붙인 필드는 보호 필드로 취급해서 클래스의 외부 사용자들이 신중하게 다뤄야 함을 의미한다.**

하지만 파이썬을 처음 접하는 많은 프로그래머가 서브클래스나 외부에서 접근하면 안 되는 내부 API를 비공개 필드로 나타낸다.

```python
class MyClass:
    def __init__(self, value):
        self.__value = value

    def get_value(self):
        return str(self.__value)

foo = MyClass(5)
assert foo.get_value() == '5'
```

이 접근방식은 잘못 되었다. 여러분을 포함해 누군가는 클래스에 새 동작을 추가하거나 기존 메소드의 결함을 해결하기 위해서(위 예제에서는 _get\_value_ 메소드가 항상 문자열을 반환하도록 한다) 서브클래스를 만들기 마련이다. **비공개 속성을 선택하면 서브클래스의 오버라이드(override)와 학장(extension)을 다루기 어렵고 불안정하게 만든다. 게다가 나중에 만들 서브클래스에서 꼭 필요하면 여전히 비공개 필드에 접근할 수 있다.


```python
class MyIntegerSubclass(MyClass):
    def get_value(self):
        return int(self._MyClass__value)
    
foo = MyIntegerSubclass(5)
assert foo.get_value() == 5
```

지금이야 동작하지만 나중에 클래스의 계층이 변경되면 MyIntegerSubclass 같은 클래스는 비공개 참조가 더는 유효하지 않게 되어 동작하지 않을 수 있다. 이 클래스가 나중에 다른 클래스를 상속받을지 누가 알 수 있겠는가?

예를 들어서 _MyIntegerSubclass_ 의 직계 부모인 _MyClass_ 에 _MyBaseClass_ 라는 또 다른 부모 클래스를 추가했다고 하자.


```python
class MyBaseClass:
    def __init__(self, value):
        self.__value = value
    # ...

class MyClass:
    pass


class MyIntegerSubclass(MyClass):
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return int(self._MyClass__value)


foo = MyIntegerSubclass(5)
assert foo.get_value() == '5'

AttributeError: 'MyIntegerSubclass' object has no attribute '_MyClass__value'
```

바뀐 상속관계 속에서 *\_\_value* 속성을 _MyClass_ 가 아닌 _MyBaseClass_ 에서 할당한다. 그러면 _MyIntegerSubclass_ 에 있는 비공개 변수 참조인 _self.\_My\_\_value_ 가 존재하지 않기 때문에 동작하지 않는다.


<Br>

## 3. 해결책: 보호 속성을 사용하자.

일반적으로 **비공개가 아닌 보호 속성을 사용해서 서브클래스가 더 많은 일을 할 수 있게 하는 편이 낫다.** 각각의 보호 필드를 문서화해서 서브클래스에서 내부 API 중 어느 것을 쓸 수 있고 어느 것을 그대로 둬야하는지 설명하자. 이렇게 하면 자신이 작성한 코드를 미래에 안전하게 확장하는 지침이 되는 것처럼 다른 프로그래머에게도 조언이 된다.

```python
class MyClass:
    def __init__(self, value):
        # 객체를 표현하는 값을 설정
	# 문자열로 강제할 수 있는 값이어야 하며(__str__ 구현)
	# 객체에 할당하고 나면 불변으로 취급해야 한다.
        self._value = value
```

반대로 비공개 속성을 사용할지 진지하게 고민할 시점은 서브클래스와 이름이 충돌할 염려가 있을 때뿐이다. 이 문제는 자식 클래스가 부지불식간에 부모클래스에서 이미 정의한 속성을 정의할 때 일어난다.


```python
class ApiClass:
    def __init__(self):
        self._value = 5

    def get(self):
        return self._value


class Child(ApiClass):
    def __init__(self):
        super().__init__()
        self._value = 'hello' # _value 속성이 겹침!

c = Child()
print(c.get(), 'and', c._value, 'should be different')
```

이런 문제는 주로 클래스가 공개 API의 일부일 때 문제가 되며 특히 속성 이름이 value 처럼 아주 일반적일 때 일어날 확률이 특히 높다. 이런 상황이 일어날 위험을 줄이려면 부모 클래스에서 비공개 속성을 사용해서 자식 클래스와 속성 이름이 겹치지 않게 하면 된다.

```python
class ApiClass:
    def __init__(self):
        self.__value = 5

    def get(self):
        return self.__value


class Child(ApiClass):
    def __init__(self):
        super().__init__()
        self._value = 'hello' # 겹치지 않음!

c = Child()
print(c.get(), 'and', c._value, 'should be different')

5 and hello should be different
```

<br>

## 4. 핵심 정리

* 파이썬 컴파일러는 비공개 속성을 엄격하게 강요하지 않는다.
* 서브클래스가 내부 API와 속성에 접근하지 못하게 막기보다는 처음부터 내부 API와 속성으로 더 많은 일을 할 수 있게 하자.
* 비공개 속성에 대한 접근을 강제로 제어하지 말고 보호 필드를 문서화해서 서브클래스에 필요한 지침을 제공하자.
* 직접 제어할 수 없는 서브클래스와 이름이 충돌하지 않게 할 때만 비공개 속성을 사용하고, 웬만하면 보호 속성을 사용하자.
