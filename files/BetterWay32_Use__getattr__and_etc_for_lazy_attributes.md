## Better Way 32. 지연 속성에는 \_\_getattr\_\_, \_\_getattribute\_\_, \_\_setattr\_\_ 을 사용하자

#### 151쪽

* Created : 2019/06/06
* Modified: 2019/06/06

<br>

## 1. 지연 속성에 유리한 \_\_getattr\_\_ 

파이썬의 언어 후크(language hook)를 이용하면 시스템들을 연계하는 범용 코드를 쉽게 만들 수 있다. 예를 들어 데이터베이스의 로우를 파이썬 객체로 표현한다고 하자. 일반적인 관계형 데이터베이스에는 스키마 세트가 있다. 그러므로 로우에 대응하는 객체를 사용하는 코드는 데이터베이스 형태도 알아야 한다.  

하지만 파이썬에서는 객체와 데이터베이스를 연결하는 코드에서 로우의 스키마를 몰라도 된다. 코드를 범용으로 만들기만 하면 된다.  

이런 일을 하는 데 적합한 클래스 매직 메소드로 \_\_getattr\_\_가 있다. **클래스에 \_\_getattr\_\_ 메소드를 정의하면 객체의 인스턴스 딕셔너리에 속성을 찾을 수 없을 때마다 이 메소드가 호출된다.**

```python
class LazyDB:
    def __init__(self):
        self.exists = 5

    def __getattr__(self, name):
        value = 'value for ' + name
        setattr(self, name, value)
        return value

lazy = LazyDB()
print('Before:', lazy.__dict__)
print('foo   :', lazy.foo)
print('After :', lazy.__dict__)

Before: {'exists': 5}
foo   : value for foo
After : {'exists': 5, 'foo': 'value for foo'}
```

LazyDB 클래스에서는 필수적인 _exists_ 속성만 미리 로드해놓는다. 그러다가 아직 로드되지 않은  _name_ 이라는 이름의 속성이 필요해질 때면, 그에 맞는 값을 _setattr_ 내장함수를 통해 설정하고, 그 값을 반환한다. **\_\_getattr\_\_ 내장함수는 인스턴스에 없는 속성을 참조할 때만 실행된다.** 이를 통해 지연 속성 할당이 가능하다.


이번에는 LazyDB를 상속해서 실제로 \_\_getattr\_\_ 메소드가 실행되는 지점의 로그를 찍는 클래스를 만들어보자.


```python
class LoggingLazyDB(LazyDB):
    def __getattr__(self, name):
        print('__getattr__ is called ')
        return super().__getattr__(name)

data = LoggingLazyDB()
print('Before:', data.__dict__)
print('foo   :', data.foo)
print('After :', data.__dict__)


Before: {'exists': 5}
__getattr__ is called 
foo   : value for foo
After : {'exists': 5, 'foo': 'value for foo'}
```

_LazyDB_ 를 상속받는 _LoggingLazyDB_ 는 \_\_getattr\_\_ 메소드를 오버라이드해서 메소드가 호출되는 순간에 로그를 찍는다.  

호출식에서 _foo_ 속성은 원래 로드되어 있지 않았다. 없는 속성을 호출하는 순간 메소드가 호출되었고 부모 클래스에서 설정한대로 _setattr_ 함수를 통해 속성을 설정한 뒤 그 값을 반환한다. 여기서 메소드는 단 한 번 속성이 존재하지 않을 때만 호출되는 것을 확인할 수 있다. 

이런 동작은 스키마리스 데이터(schemaless data)에 지연 접근하는 경우에 특히 도움이 된다. **\_\_getattr\_\_ 이 I/O를 동반할 수도 있는 프로퍼티 로딩이라는 어려운 작업을 한 번만 실행하면 다음 접근부터는 기존 결과를 가져온다.**


<br>

## 2. 지연 속성에 대한 전역 검색: \_\_getattribute\_\_

데이터베이스 시스템에서 트랜잭션도 원한다고 하자. 사용자가 다음 번에 속성에 접근할 때는 대응하는 데이터베이스의 로우가 여전히 유효한지, 트랜잭션이 여전히 열려 있는지 알고 싶다고 하자. **\_\_getattr\_\_ 후크는 기존 속성에 빠르게 접근하려고 객체의 인스턴스 딕셔너리를 사용하는 데 그치지 때문에 이 작업에는 믿고 쓸 수 없다.**

이런 쓰임새를 위해서는 비슷하지만 다른 \_\_getattribute\_\_ 라는 또 다른 후크를 사용할 수 있다. **이 특별한 메소드는 객체의 속성에 접근할 때마다 호출되며, 심지어 해당 속성이 속성 딕셔너리에 있을 때도 호출된다.** \_\_getattr\_\_ 메소드가 속성이 없을 때만 호출되는 것과는 대조적이다.  

이런 동작 덕분에 속성에 접근할 때마다 전역 트랜잭션 상태를 확인하는 작업 등에 쓸 수 있다. 여기서는 이 메소드가 호출될 때마다 로그를 남기려고 ValidatingDB를 정의한다.

```python
class ValidatingDB:
    def __init__(self):
        self.exists = 5

    def __getattribute__(self, name):
        print('__getattribute__ called with', name)
        try:
            return super().__getattribute__(name)
        except AttributeError:
            value = 'value for ' + str(name)
            setattr(self, name, value)
            return value

data = ValidatingDB()
print('Before:', data.__dict__)
print('foo   :', data.foo)
print('After :', data.__dict__)


__getattribute__ called with __dict__
Before: {'exists': 5}
__getattribute__ called with foo
foo   : value for foo
__getattribute__ called with __dict__
After : {'exists': 5, 'foo': 'value for foo'}
```

\_\_getattr\_\_ 를 구현한 _LoggingLazyDB_ 와 코드가 비슷하지만 차이가 있다. **\_\_getattribute\_\_ 메소드는 인스턴스에 속성이 있어도, 없어도 항상 호출된다.** 따라서 인스턴스의 일반 속성이든, 지연 속성이든 전역적으로 속성 검사를 할 수 있다.

<br>

**만약 동적으로 접근한 속성이 존재하지 않아야 하는 경우에는 AttributeError를 일으켜서 \_\_getattr\_\_, \_\_getattribute\_\_에 속성이 없는 경우의 파이썬 표준 동작이 일어나게 한다.**

```python
class MissingPropertyDB:
    def __getattr__(self, name):
        if name == 'bad_name':
            raise AttributeError(name + " is not permitted here")

data = MissingPropertyDB()
data.bad_name


AttributeError: bad_name is not permitted here
```

<br>

또 다른 특징을 살펴보자. 파이썬 코드로 범용적인 기능을 구현할 때 종종 내장함수 _hasattr_ 로 프로터리가 있는지 확인하고 내장 함수 _getattr_ 로 프로퍼티 값을 가져온다. **이 함수들도 \_\_getattr\_\_을 호출하기 전에 인스턴스 딕셔너리에서 속성 이름을 찾는다.**

```python
data = LoggingLazyDB()

print('Before:', data.__dict__)
print('foo exists?', hasattr(data, 'foo'))
print('foo   :', data.foo)
print('After :', data.__dict__)
print('foo exists?', hasattr(data, 'foo'))


Before: {'exists': 5}
__getattr__ is called 
foo exists? True
foo   : value for foo
After : {'exists': 5, 'foo': 'value for foo'}
foo exists? True
```

아까의 _LoggingLazyDB_ 예제에서 _foo_ 라는 속성이 존재하는지 _hasattr_ 내장 함수를 통해 확인하는 print문만 추가했다.

_data_ 를 처음 생성할 때는 _foo_ 속성은 아직 존재하지 않는다. 따라서 두 번째 print문의 _hasattr_ 문이 False가 나올 것이라 예상할 수 있는데 신기하게 True가 나온다. 즉, **hasattr문 내부에서는 \_\_getattr\_\_ 가 호출되고, LazyDB 클래스의 \_\_getattr\_\_ 메소드는 호출되면서 없는 속성을 그 자리에서 할당하기 때문에 결과적으로 True가 반환된 것이다.**


<br>

## 3. 지연 속성 할당: \_\_setattr\_\_


앞선 두 메소드가 어떤 식으로든 속성을 불러오는데, 즉 로드하는 데 관심이 있었는데 이번에는 **반대로 지연 방식으로 데이터를 데이터베이스에 집어넣고 싶다고 하자.**

이 작업은 **임의의 속성 할당을 가로채는 \_\_setattr\_\_ 언어 후크로 달성할 수 있다. \_\_getattr\_\_, \_\_getattribute\_\_이 속성을 가져오되 조금 다른 성질을 갖고 있는 데 반해 이 메소드는 별도의 두 메소드 대신 이 메소드 하나만 쓰면 된다.**

**\_\_setattr\_\_ 메소드는 인스턴스의 속성이 할당을 받을 때마다 직접 혹은, 내장 함수 setattr을 통해 호출된다.**

```python
class SavingDB:
    def __setattr__(self, name, value):
        # DB에 데이터를 저장하는 로직
        super().__setattr__(name, value)

class LoggingSavingDB(SavingDB):
    def __setattr__(self, name, value):
        print('called with', name, value)
        super().__setattr__(name, value)


Before: {}
called with foo 5
After : {'foo': 5}
called with foo 7
Finally : {'foo': 7}
```

처음에 만든 LoggingSavingDB 인스턴스는 따로 속성을 갖고 있지 않다. 그 다음에 _foo_ 를 5로 설정하는 코드와 _foo_ 를 7로 재할당하는 코드에서 모두 \_\_setattr\_\_ 가 호출됐다.  

\_\_setattr\_\_는 \_\_getattr\_\_와 이름이 비슷하기에 \_\_getattr\_\_ 처럼 속성이 없을 때만 호출되리라 예상할 수 있는데 의외다. **속성이 있을 때, 없을 때 모두 호출되는 \_\_getattribute\_\_처럼 속성을 할당한다는 것을 알 수 있었다.**


<br>

## 4. 무한 재귀의 위험성

**\_\_getattribute\_\_, \_\_setattr\_\_을 사용할 때 종종 부딪히는 문제는 객체의 속성에 접근할 때마다(심지어 원하지 않을 때도) 호출된다는 점이다.** 예를 들어 객체의 속성에 접근하면 실제로 연관 딕셔너리에서 키를 찾게 하고 싶다고 하자.


```python
class BrokenDictionaryDB:
    def __init__(self):
        self._data = {}

    def __getattribute__(self, name):
        print('__getattribute__ called with', name)
        return self._data[name]


data = BrokenDictionaryDB()
data.foo

__getattribute__ called with foo
__getattribute__ called with _data
__getattribute__ called with _data
__getattribute__ called with _data

RecursionError: maximum recursion depth exceeded while calling a Python object
```

이 문제는 \_\_getattribute\_\_가 _self.\_data_ 에 접근하면 \_\_getattribute\_\_ 가 다시 실행되고, 다시 *self.\_data* 에 접근한다는 정미다.  

이에 대한 **해결책은 인스턴스에서 super().\_\_getattribute\_\_ 메소드로 인스턴스 속성 딕셔너리에서 값을 얻어오는 것이다. 이렇게 하면 재귀호출을 피할 수 있다.**

```python
class DictionaryDB:
    def __init__(self, data):
        self._data = data

    def __getattribute__(self, name):
        data_dict = super().__getattribute__('_data')
        return data_dict[name]
```

마찬가지의 이유로 **객체의 속성을 수정하는 \_\_setattr\_\_ 메소드에서도 super().\_\_setattr\_\_을 사용해야 한다.**


<Br>

## 5. 핵심 정리

* 객체의 속성을 지연(lazy) 방식으로 로드하고 저장하려면 \_\_getattr\_\_, \_\_setattr\_\_을 사용하자.
* \_\_getattr\_\_ 은 존재하지 않는 속성에 접근할 때 한 번만 호출되는 반면에 \_\_getattribute\_\_ 는 속성에 접근할 때마다 호출된다는 점을 이해하자.
* \_\_getattribute\_\_와 \_\_setattr\_\_ 에서 인스턴스 속성에 직접 접근할 때 super()(즉, object 클래스)의 메소드를 사용하여 무한 재귀가 일어나지 않게 하자.
