# 114쪽. 믹스인 유틸리티 클래스에만 다중 상속을 사용하자.
# 2017/06/20 작성.
  
**코드 내용이 꽤 어렵다. 주의 깊게 보기를 권한다**  
<br>

## Part 1.
파이썬은 다중 상속을 쉽게 사용하도록 지원한다. 하지만 다중 상속은 아예 안 하는 게 좋다.  
다중 상속으로 얻는 편리함과 캡슐화가 필요하면 대신 믹스인(mix-in)을 작성하는 방안을 활용하자.  
믹스인이란 **클래스에서 제공해야 하는 추가적인 메서드만 정의한 작은 클래스**로서,  
자체 인스턴스 속성을 갖지 않으며, \_\_init\_\_ 를 작성 안 해도 된다.  
이 믹스인은 장고 CBV(Class Based View)에 폭넓게 구현되어 있는데 참고하기 바란다.  

<br>
파이썬에서는 타입과 상관없이 객체의 현재 상태를 간단히 조사할 수 있어 믹스인을 쉽게 작성할 수 있다.  
동적 조사(dynamic inspection, 예를 들면 hasattr, isinstnace 등)를 통해  
많은 클래스에 적용할 수 있는 범용 기능을 믹스인에 한 번만 작성하면 된다.  
믹스인을 조합하고 계층으로 구성하면 반복 코드를 최소화하고 재사용성을 극대화할 수 있다.  

<br><br>
본격적인 예를 살펴보자.  
예를 들어 파이썬 객체를 메모리 내부 표현에서 직렬화용 딕셔너리로 변환하는 기능이 필요하다.  
이 기능을 모든 클래스에서 사용할 수 있도록 범용으로 작성할 수 있을까?  
```python
class ToDictMixin:
    def to_dict(self):
        return self._traverse_dict(self.__dict__)

    def _traverse_dict(self, instance_dict):
        ouput = {}
	for key, value in instance_dict.items():
	    output[key] = self._traverse(key, value)
	return output

    def _traverse(self, key, value):
        if isinstance(value, ToDictMixin):
	    return value.to_dict()
	elif isinstance(value, dict):
	    return self._traverse_dict(value)
	elif isinstance(value, list):
	    return [self._traverse(key, i) for i in value]
	elif hasattr(value, '__dict__'):
	    return self._traverse_dict(value.__dict__)
	else:
	    return value
```

<br>

코드가 꽤나 어렵다. 이 믹스인 클래스는 상속하는 다른 클래스들의 속성을 직렬화용 딕셔너리로 반환한다.  
코드에 대해 설명하기 전에 **\_\_dict\_\_**, 이것에 대해 알아보면,  
클래스 인스턴스는 여러 attribute, member를 갖는데, **인스턴스의 \_\_dict\_\_ 속성은 나머지 속성들을 모아**
**딕셔너리로 반환한다.** 

<br>

```python

class Test:
    def __init__(self):
        self.a = 1
	self.b = 2
	self.c = 3

t = Test()
print(t.__dict__)


>>> {'a': 1, 'b': 2, 'c': 3}
```
  

즉 이 코드는 클래스의 속성과 그 값들을 딕셔너리로 반환하는 코드이다.  
하지만 _traverse와 _traverse_dict에서 꽤나 버벅거리게 하는데 이유가 있다.  
우리는 가능한 모든 객체에서 작동하는 직렬화 믹스인을 만들고 있고, 각 객체가 가지고 있는  
속성값의 종류는 천차만별일 것이다. 정수, 소수, 리스트, 딕녀서리, 다른 객체 등등..  
그렇기 때문에 그 값들에 모두 대응해주기 위해 여러 타입 검사 과정 등을 거치는 것이다.  

또한 _traverse, _traverse_dict는 서로를 반환값으로 사용하는 경우가 있는데, 이는 직렬화용 딕셔너리가  
보통 중첩되는 경우가 많고 딕셔너리의 원소가 리스트, 딕셔너리일 때 각 원소를 또 다시 재귀적으로   
딕셔너리화해서 하나의 큰 딕셔너리를 만들기 때문이다. 이 코드는 정말 감탄이 나오는 코드인데,  
계속 공부해야 할 것 같다.   

<br><br>

이제는 실례로, 바이너리 트리를 딕셔너리로 표현하기 위해 믹스인을 사용하는 예제이다.

```python
class BinaryTree(ToDictMixin):
    def __init__(self, value, left=None, right=None):
        self.value = value
	self.left = left
	self.right = right

tree = BinaryTree(10,
	left=BinaryTree(7, right=BinaryTree(9)),
	right=BinaryTree(13, left=BinaryTree(11)))

print(tree.to_dict())


>>> 

{'left': {'left': None,
          'right': {'left': None, 'right': None, 'value': 9},
	            'value': 7},
 'right': {'left': {'left': None, 'right': None, 'value': 11},
	'right': None,  'value': 13},
 'value': 10}


```

이진 트리가 딕셔너리로 표현된 것을 볼 수 있다.  
이렇게 경이로울 수가 있다... 트리를 딕셔너리로 표현한다...   
이것을 이렇게 아름답게 코드로 옮길 수 있는 사람이 몇이나 있을까..

<br><br><br>


## Part 2.
믹스인의 장점은 범용 기능을 교체할 수 있게 만들어서 필요할 때 동작을 오버라이드할 수 있다는 점이다.   
예를 들어 다음은 부모 노드에 대한 참조를 저장하는 **BinaryTree**의 서브클래스이다.

```python
class BinaryTreeWithParent(BinaryTree):
    def __init__(self, value, left=None,
                 right=None, parent=None):
        super().__init__(value, left=left, right=right)
	self.parent = parent
```

이 트리 클래스는 이전 클래스를 상속해 다른 정보들과 함께 부모 노드에 대한 정보도 저장한다.  
그렇게 ToDictMixin.to_dict의 기본 구현은 이 클래스를 무한 루프에 빠지게 한다.  
왜인지 알겠는가?(난 이거 1시간 보고 이해했다... ㅠㅠ)  

왜냐하면 이전에는 왼쪽, 오른쪽 자식 노드만 정보를 가지고 있었는데 이제는 부모에 대한  
정보까지 딕셔너리로 만들어야 하고 부모는 또 자식을 딕셔너리로 찾으니 순환참조가 발생하는 것이다.  
해결책은 BinaryTreeWithParent 클래스에서 ToDictMixin._traverse 메서드를 오버라이드해서  
믹스인이 순환에 빠지지 않게 필요한 값만 처리하는 것이다.  
다음은 메서드를 오버라이드해서 부모를 탐색하지 않고 부모의 value만 가져오도록 만들었다.  


```python

def _traverse(self, key, value):
    if isinstance(value, BinaryTreeWithParent) and key == 'parent':
        return value.value
    else:
	return super()._traverse(key, value)

```

순환 참조 속성을 따라가지 않으므로 BinaryTreeWithParent.to_dict는 문제없이 작동한다.


<br><BR><br>
## Part 3.
여러 믹스인을 조합할 수도 있다.  
예를 들어 어떤 클래스에도 동작하는 범용 JSON 직렬화를 제공하는 믹스인이 필요하다고 하자.  
이 믹스인은 클래스에 to_dict가 있다고 가정하고 만들면 된다.  


이 코드도 꽤나 어렵다.. 차분히 바라보자


```python
import json

class JsonMixin:
    @classmethod
    def from_json(cls, data):
        kwargs = json.loads(data)
	return cls(**kwrags)

    def to_json(self):
        return json.dumps(self.to_dict())
```

JsonMixin 클래스가 어떻게 인스턴스 메서드와 클래스 메서드를 둘 다 정의하는지 주목하자.  
믹스인을 이용하면 이 두 종류의 동작을 추가할 수 있다.  
이 예제에서 JsonMixin의 요구 사항은

* 클래스에 to_dict 메서드가 있고,(to_json)
* 해당 클래스의 \_\_init\_\_ 메서드에서 키워드 인수를 받는다는 것이다.(from_json)

이 믹스인을 이용하면 짧은 반복 코드로 JSON을 직렬화하고 JSON에서 역직렬화하는  
유틸리티 클래스의 계층 구조를 간단하게 생성할 수 있다. 다음 예를 살펴보자.


```python
class DataCenterRack(ToDictMixin, JsonMixin):
    def __init__(self, swith=None, machines=None):
        self.switch = Switch(**switch)
	self.machines = [Machine(**kwargs) for kwargs in machines]

class Switch(ToDictMixin, JsonMixin):
    pass

class Machine(ToDictMixin, JsonMixin):
    pass



serialized = """{
    "switch" : {"ports": 5, "speed": 1e9},
    "machines": [
        {"cores": 8, "ram": 32e9, "disk", 5e12},
        {"cores": 4, "ram": 16e9, "disk", 1e12},
        {"cores": 2, "ram": 4e9, "disk", 500e9},
    ]
}"""


deserialized = DataCenterRack.from_json(serialized)
roundtrip = deserialized.to_json()
assert json.loads(serialized) == json.loads(roundtrip)
```

\*\*kwargs 같은 packing, unpacking은 안다고 생각하겠다.  
이런 믹스인을 사용할 때는 클래스가 객체 상속 계층의 상위에서 이미  
JsonMixin을 상속받고 있어도 괜찮다. 결과로 만들어지는 클래스는 같은 방식으로 동작할 것이다.


## 핵심정리
* 믹스인 클래스로 같은 결과를 얻을 수 있다면 다중 상속을 하지 말자.
* 인스턴스 수준에서 동작을 교체할 수 있게 만들어서 믹스인 클래스가 요구할 때  
  클래스 별로 원하는 동작을 하게 하자.
* 간단한 동작들로 복잡한 기능을 생성하려면 믹스인을 조합하자.
