## Better Way 26. 믹스인 유틸리티 클래스에만 다중 상속을 사용하자

#### 114쪽

* Created : 2017/06/20
* Modified: 2019/05/25  

<br>

## 1. Python의 믹스인


파이썬은 다중 상속을 쉽게 사용하도록 지원한다. 하지만 다중 상속은 아예 안 하는 게 좋다. 다중 상속으로 얻는 편리함과 캡슐화가 필요하면 대신 믹스인(mix-in)을 작성하는 방안을 활용하자.  

믹스인이란 **클래스에서 제공해야 하는 추가적인 메서드만 정의한 작은 클래스**로서, 자체 인스턴스 속성을 갖지 않으며, \_\_init\_\_ 생성자 메소드를 작성하지 않는다.

파이썬에서는 타입과 상관없이 객체의 현재 상태를 간단히 조사할 수 있어 믹스인을 쉽게 작성할 수 있다. 파이썬에서는 _hasattr_, _isinstance_ 등의 내장함수를 통해 객체에 대한 동적 조사를 지원하므로, 이를 통해 많은 클래스에 적용할 수 있는 범용 기능을 믹스인에 한 번만 작성할 수 있다.

믹스인을 조합하고 계층으로 구성하면 반복 코드를 최소화하고 재사용성을 극대화할 수 있다.  


본격적인 예를 살펴보자.  

예를 들어 **파이썬 객체를 메모리 내부 표현에서 직렬화용 딕셔너리로 변환하는 기능이 필요하다고 하자.**  이 기능을 말 그대로 파이썬의 모든 클래스에서 사용할 수 있도록 범용으로 작성할 수 있을까?  

다음은 상속받는 모든 클래스에 추가될 새 공개 메소드로 이 기능을 구현하는 믹스인이다.

```python
class ToDictMixin:
    def to_dict(self):
        return self._traverse_dict(self.__dict__)

    def _traverse_dict(self, instance_dict):
        output = {}
        for key, value in instance_dict.items():
            output[key] = self._traverse(key, value)
        return output

    def _traverse(self, key, value):
        if isinstance(value, ToDictMixin):
            return value.to_dict()
        elif isinstance(value, dict):
            return self._traverse_dict(value)
        elif isinstance(value, list):
            return [self._traverse(key, v) for v in value]
        elif hasattr(value, '__dict__'):
            return self._traverse_dict(value.__dict__)
        else:
            return value
```

**_ToDictMixin_ 클래스는 _to\_dict_ 외부 인터페이스를 갖는데 이 클래스는 인스턴스 자체를 탐색해 JSON으로 변환할 _dict_ 를 반환한다.** 그리고 인스턴스를 탐색해 가지고 있는 속성과 행동을 재귀호출해서 _dict_ 형태로 반환하는 내부 인터페이스 _\_traverse\_dict_ 메소드와 _\_traverse_ 메소드를 보유하고 있다.

_\_traverse_ 코드가 상당히 복잡하다. 처음에 이 부분에 골머리를 앓았는데 다 그럴만한 이유가 있다. _to\_dict_ 메소드는 파이썬의 모든 클래스에서 사용할 수 있도록 범용적이어야 한다. _to\_dict_ 메소드가 _ToDictMixin_ 를 상속받는 클래스뿐 아니라 상속받지 않는 클래스도 _dict_ 로 만들어야 할 수 있어야 한다는 뜻이다.

파이썬에서 값을 담는 _Container_ 원시 클래스(ABC)는 일종의 트리 구조로 계층구조를 구성할 수 있다. _dict_ 는 _Container_ 를 상속받기 때문에 이 특징을 공유한다. 이런 상황에서 _to\_dict_ 를 구현한 클래스의 인스턴스가 갖고 있는 속성은 어떤 타입이든지 될 수 있기 때문에 _to\_dict_ 메소드를 갖고 있으리라 합리적으로 기대할 수 없다. 즉, 각 속성 또한 결국엔 인스턴스이고 자신들의 속성을 무수히 많이 가질 수 있기 때문에 각 값들에 대한 대응을 위해 복잡해질 수 없었다. 항상 강조하지만, **복잡도와 자유도는 함께 간다.** 복잡해졌기 때문에 특정 클래스에 얽매이지 않을 수 있는 것이다.

<br>

이를 활용한 예를 만들어보자. JSON은 _dict_ 와 유사한데 _dict_ 는 트리로 계층구조를 가질 수 있다고 했다. 실제로 BinaryTree 자료구조를 만들어보자. BinaryTree 자료구조는 가지를 오른쪽, 왼쪽 한 쌍의 값만 갖는 트리구조다.

```python
class BinaryTree:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
```

이제 수많은 관련 파이썬 객체를 딕셔너리로 손쉽게 변환할 수 있다.

```python
tree = BinaryTree(10,
                  left=BinaryTree(7,
                                  right=BinaryTree(9)
                                 ),
                  right=BinaryTree(13,
                                   left=BinaryTree(11)
                                  )
                 )

print(tree.to_dict())


# 결과는 트리 구조를 나타내기 위해 들여쓰기함
{'left': {'left': None,
          'right': {'left': None,
                    'right': None,
                    'value': 9},
          'value': 7},
 'right': {'left': {'left': None,
                    'right': None,
                    'value': 11},
           'right': None,
           'value': 13},
 'value': 10}
```


믹스인의 가장 큰 장점은 범용 기능을 교체할 수 있게 만들어서 필요할 때 동작을 오버라이드할 수 있다는 점이다. 예를 들어 작성한 이진트리 클래스를 확장해서 양쪽 노드뿐 아니라 부모 노드에 대한 참조까지 저장하는 클래스를 만들자.

```python
class BinaryTreeWithParent(BinaryTree):
    def __init__(self, value, left=None,
                 right=None, parent=None):
        super().__init__(value, left=left, right=right)
        self.parent = parent
```

이 클래스의 인스턴스에 _to\_dict_ 메소드를 쓰면 무한루프에 빠지게 된다. _self.parent_ 를 _dict_ 로 만들 때 오른쪽이든, 왼쪽이든지 간에 위치할 자기 자신을 참조하기 때문이다.

해결책은 간단하다. _BinaryTreeWithParnet_ 클래스에서 _ToDictMixin.\_traverse_ 메소드만 오버라이드해 순환에 빠지지 않도록 살짝만 변경해주면 된다.

```python
class BinaryTreeWithParent(BinaryTree):
    def __init__(self, value, left=None,
                 right=None, parent=None):
        super().__init__(value, left=left, right=right)
        self.parent = parent

    def _traverse(self, key, value):
        # 속성 이름이 'parent'일 시 재귀호출하지 않고 바로 값을 반환
        if isinstance(value, BinaryTreeWithParent) and key == 'parent':
            return value.value
        else:
            return super()._traverse(key, value)
```

부모 클래스의 _\_traverse_ 메소드를 확장해서 인스턴스의 속성 이름이 'parent'일 시 재귀호출하지 않고 바로 값만을 반환하게 수정했다. 코드는 문제없이 작동한다.

```python
root = BinaryTreeWithParent(10)
root.left = BinaryTreeWithParent(7, parent=root)
root.left.right = BinaryTreeWithParent(9, parent=root.left)
print(root.to_dict())


# 결과는 트리 구조를 나타내기 위해 가공함
{'value': 10,
 'parent': None,
 'left': {'value': 7,
	  'parent': 10}, 
          'left': None,
	  'right': {'value': 9,
		    'parent': 7,
	            'left': None,
		    'right': None},
 'right': None}
```

이는 추가적인 이점도 있는데 **_BinaryTreeWithParent_ 인스턴스 자신뿐 아니라 이 인스턴스를 속성으로 갖는 다른 무관한 인스턴스에도 자동으로 _ToDictMixin_ 의 기능이 적용된다는 점이다.**

```python
class NamedSubTree(ToDictMixin):
    def __init__(self, name, binarytreeparent_instance):
        self.name = name
        self.binarytreeparent_instance = binarytreeparent_instance


my_tree = NamedSubTree('foobar', root.left.right)
print(my_tree.to_dict())

# NamedSubTree 또한 무한루프의 영향을 받지 않음.
{'name': 'foobar',
 'binarytreeparent_instance': {'value': 9,
                               'left': None,
                               'right': None,
                               'parent': 7}}
```

<br>

## 2. 믹스인 다중 상속

시작하면서 다중 상속은 가급적 믹스인을 대상으로만 하는 것이 좋다고 했다. 그 예를 만들어보자. 앞서 작성한 _ToDictMixin_ 믹스인에 추가로 어떤 클래스에도 동작하는 범용 JSON 직렬화 기능 믹스인이 필요하다고 해보자. 또한 이 믹스인은 클래스에 _ToDictMixin_ 의 _to\_dict_ 메소드가 있다고 가정한다고 하자.

먼저 JSON 직렬화 기능을 구현하는 _JsonMixin_ 를 구현하자.

```python
import json

class JsonMixin:
    @classmethod
    def from_json(cls, data):
        kwargs = json.loads(data)
        return cls(**kwargs)  # 1.

    def to_json(self): # 2.
        return json.dumps(self.to_dict())
```

_JsonMixin_ 클래스가 어떻게 인스턴스 메소드와 클래스 메소드를 둘 다 정의하는지 주목하자. 믹스인을 이용하면 두 종류의 동작을 추가할 수 있다. 이 예제에서 _JsonMixin_ 의 요구사항은 클래스에 _to\_dict_ 메소드가 있고(\# 1.), 해당 클래스의 \_\_init\_\_ 메소드에서 키워드 인자를 받는다는 것뿐이다.(\# 2.)

이 믹스인을 이용하면 짧은 반복 코드로 JSON으로 직렬화하고 역직렬화하는 유틸리티 클래스의 계층구조를 간단하게 생성할 수 있다. 예를 들어 다음은 데이터센터 토폴로지를 구성하는 부분들을 표현하는 데이터 클래스의 계층이다.

```python
class DatacenterRack(ToDictMixin, JsonMixin):
    def __init__(self, switch=None, machines=None):
        self.switch = Switch(**switch)
        self.machines = [Machine(**kwargs) for kwargs in machines]

class Switch(ToDictMixin, JsonMixin):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class Machine(ToDictMixin, JsonMixin):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
```

두 믹스인을 상속받는 클래스에는 두 가지 요구사항이 있었는데:

1. _to\_dict_ 메소드를 가지고 있고
1. **해당 클래스의 \_\_init\_\_ 메소드에서 키워드 인자를 받아 각 key와 value를 인스턴스의 속성으로 설정할 수 있어야 한다.**

2번째 요구사항을 지키기 위해 둘 모두를 상속하는 _Switch_ 와 _Machine_ 클래스에서 _setattr_ 내장함수를 통해 _key_ 를 이름으로 갖는 속성에 _value_ 를 할당했다.

이 클래스들을 JSON으로 직렬화하고 역직렬화하는 방법은 간단하다. 여기서는 데이터가 직렬화와 역직렬화를 통해 원래 상태가 되는지 검증하자.

```python
serialized = """{
  "switch": {"ports": 5, "speed": 1e9},
  "machines": [
    {"cores": 8, "ram": 32e9, "disk": 5e12,
     "cores": 4, "ram": 16e9, "disk": 1e12,
     "cores": 2, "ram": 4e9,  "disk": 500e9}
  ]
}"""


deserialized = DatacenterRack.from_json(serialized)
rountrip = deserialized.to_json()

assert json.loads(serialized) == json.loads(rountrip)
```

복잡한 코드 없이 상속을 통해 정확하게 동작함을 볼 수 있다.

<Br>


## 3. 핵심 정리

* 믹스인 클래스로 같은 결과를 얻을 수 있다면 다중 상속을 사용하지 말자.
* 인스턴스 수준에서 동작을 교체할 수 있게 만들어서 믹스인 클래스가 요구할 때 클래스별로 원하는 동작을 하게 하자.
* 간단한 동작들로 복잡한 기능을 생성하려면 믹스인을 조합하자.
