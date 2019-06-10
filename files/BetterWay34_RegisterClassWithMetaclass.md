## Better Way 34. 메타클래스로 클래스의 존재를 등록하자

#### 161쪽

* Created : 2019/06/10
* Modified: 2019/06/10


<br>

## 1. JSON 직렬화, 역직렬화 클래스 만들기

**메타클래스를 사용하는 또 다른 일반적인 사례는 프로그램에 있는 타입을 자동으로 등록하는 것이다. 등록(Registration)은 간단한 식별자(Identifier)를 대응하는 클래스에 매핑하는 역방항 조회(Reverse lookup)를 수행할 때 유용하다.**

예를 들어 파이썬 객체를 직렬화한 표현을 JSON으로 구현한다고 해보자. 객체를 얻어와서 JSON 문자열로 변환할 방법이 필요하다.

다음은 생성자 메소드의 인자를 저장하고 JSON 딕셔너리로 변환하는 기반 클래스를 범용적으로 정의한 것이다.

```python
import json

class Serializable:
    def __init__(self, *args):
        self.args = args

    def serialize(self):
        return json.dumps({'args': self.args})
```

매우 간단한 클래스로서 서브클래스들의 초기화 인자를 JSON으로 직렬화할 메소드 _serialize_ 를 가지고 있다. 이 클래스를 이용하면 가령 '2차원 점'에 대응하는 간단한 불변 자료구조를 문자열로 쉽게 직렬화할 수 있다.

```python
class Point2D(Serializable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Point2D({self.x}, {self.y})'

point = Point2D(5, 3)
print('Point     :', point)
print('Serialized:', point.serialize())


Point     : Point2D(5, 3)
Serialized: {"args": [5, 3]}
```

JSON 객체를 문자열로 변환하는 직렬화가 잘 작동함을 확인할 수 있다. 이제 반대로 이 문자열을 역직렬화해서 JSON이 표현하는 Point2D 객체를 생성하자. 많은 방법이 있겠지만 여기서는 _Serializable_ 를 상속받는 또 다른 클래스를 정의한다.

```python
class Deserializable(Serializable):
    @classmethod
    def deserialize(cls, json_data):
        params = json.dumps(json_data)
        return cls(parms['args'])
```

_Deserializable_ 을 이용하면 간단한 불변 객체들을 범용적인 방식으로 쉽게 직렬화하고 역직렬화할 수 있다.

```python
class BetterPoint2D(Deserializable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Point2D({self.x}, {self.y})'

point = BetterPoint2D(7, 5)
print('Before    :', point)
data = point.serialize()
print('Serialized:', data)
after = BetterPoint2D.deserialize(data)
print('After     :', after)


Before    : Point2D(7, 5)
Serialized: {"args": [7, 5]}
After     : Point2D(7, 5)
```

_BetterPoint2D_ 객체를 문자열로 직렬화하고, 반대로 역직렬화까지 성공적으로 변환했다. 이 방법은 잘 작동하지만, **직렬화된 데이터에 대응하는 타입(예를 들어 Point2D, BetterPoint2D)을 미리 알고 있을 때만 동작한다는 문제점이 있다.** 그 이유는 역직렬화 함수가 특정 클래스에 바운딩되어 있기 때문이다.

클래스를 써야하는 복잡한 현실상황이라면 이상적으로는 **JSON으로 직렬화되는 많은 클래스를 갖추고 그중 어떤 클래스든 대응하는 파이썬 객체로 역직렬화하는 공통 함수를 하나만 두려고 할 것이다.**

이렇게 만들려면 직렬화할 객체의 클래스 이름을 JSON 데이터에 포함하면 된다.

```python
class BetterSerializable:
    def __init__(self, *args):
        self.args = args

    def serialize(self):
        return json.dumps({
            'class': self.__class__.__name__,
            'args': self.args,
        })
```

다음으로 클래스 이름을 해당 클래스의 객체 생성자에 매핑하고 이 매핑을 관리한다.

```python
registry = {}

def register_class(target_class):
    registry[target_class.__name__] = target_class

def deserialize(data):
    parms = json.loads(data)
    name = parms['class']
    target_class = registry[name]
    return target_class(*params['args'])
```

매핑을 관리할 _dict_ 인 _registry_ 와 여기에 클래스를 등록하는 함수와 역직렬화하는 함수를 *register\_class*, _deserialize_ 함수로 각각 만들었다. 이때 기억할 것은 **이 변수와 함수들은 특정 클래스에 바운딩되어 있지 않은 글로벌 이름으로서, 다른 많은 서브클래스들에서 편하게 사용할 수 있다는 점이다.**

_deserialize_ 가 항상 제대로 동작함을 보장하려면 추후에 역직렬화할 법한 모든 클래스에서 *register\_class* 를 호출해야 한다.

```python
class EvenBetterPoint2D(BetterSerializable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y

register_class(EvenBetterPoint2D) # 클래스 등록!
```

이제 문자열 JSON 데이터가 어떤 클래스를 담고 있는지 몰라도 문제없이 역직렬화할 수 있다.

```python
Before    : EvenBetterPoint2D(100, 50)
Serialized: {"class": "EvenBetterPoint2D", "args": [100, 50]}
After     : EvenBetterPoint2D(100, 50)
```

<br>

## 2. 개선점: 메타클래스로 자동으로 등록하기

이전 장의 범용적인 역직렬화 방법도 문제점이 있다. 이 방법의 문제는 **서브클래스를 정의할 때 _register\_class_ 를 호출하는 일을 까먹을 수 있다는 점이다.**

```python
class Point3D(BetterSerializable):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.x = x
        self.y = y
        self.z = z

# 아뿔싸! 등록하는 것을 까먹어부렸다!
```

이런 실수는 충분히 할 수 있고, 이는 등록을 잊는 클래스의 객체를 런타임에 역직렬화할 때 코드가 중단되는 원인이 된다.

```python
point = Point3D(1, 2, -3)
data = point.serialize()
deserialize(data)


KeyError: 'Point3D'
```

_Point3D_ 클래스를 등록하는 것을 깜빡했기 때문에 범용 역직렬화 함수의 _registry_ 에서 목표 클래스를 찾지 못했다. 이렇게 모든 서브 클래스에서 필요한 기능을 사용자가 매번 호출하는 일은 오류가 일어날 가능성이 높으며, 특히 초보 프로그래머에게는 어렵다.  

프로그래머가 의도한 대로 **_BetterSerializable_ 을 사용하고, 수동이 아닌 모든 경우에 *register\_class* 가 호출된다고 확신하게 할 수는 없을까?** 메타클래스를 이용하면 서브클래스가 정의될 때 _class_ 문을 가로채는 방법으로 이렇게 만들 수 있다. 메타클래스로 클래스 본문이 끝나자마자 새 타입을 등록하면 된다.

```python
class SerializeMeta(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        register_class(cls)
        return cls

class RegisteredSerializable(BetterSerializable, metaclass=SerializeMeta):
    pass
```

메타클래스의 \_\_new\_\_ 메소드에서 클래스를 정의한 후 반환하기 직전 정의된 클래스를 자동 등록한다. 이렇게 하면 **_RegisteredSerializable_ 의 서브클래스를 정의할 때 *register\_class* 가 호출되어 _deserialize_ 가 KeyError를 일으키지 않고 항상 기대한 대로 동작할 것이라고 확신할 수 있다.**


```python
class Vector3D(RegisteredSerializable):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f'Vector 3D({self.x}, {self.y}, {self.z})'

v3 = Vector3D(10, -7, 100)
print('Before    :', v3)
data = v3.serialize()
print('Serialized:', data)
after = deserialize(data)
print('After     :', after)


Before    : Vector 3D(10, -7, 100)
Serialized: {"class": "Vector3D", "args": [10, -7, 100]}
After     : Vector 3D(10, -7, 100)
```

메타클래스를 이용해 클래스를 등록하면 상속 트리가 올바르게 구축되어 있는 한 클래스 등록을 놓치지 않는다. 앞에서 본 것처럼 직렬화에 잘 동작하며 ORM, 플러그인 시스템, 시스템 후크 등에도 적용할 수 있다.


<br>

## 3. 핵심 정리

* 클래스 등록은 모듈 방식의 파이썬 프로그램을 만들 때 유용한 패턴이다.
* 메타클래스를 이용하면 프로그램에서 기반 클래스로 서브클래스를 만들 때마다 자동으로 등록 코드를 실행할 수 있다.
* 메타클래스를 이용해 클래스를 등록하면 등록 호출을 절대 빠뜨리지 않으므로 오류를 방지할 수 있다.
