## Better Way 35. 메타클래스로 클래스 속성에 주석을 달자

#### 167쪽

* Created : 2019/06/11
* Modified: 2019/06/11

<br>

## 1. 일단 디스크립터로 속성을 할당할 때의 문제점: 반복

**메타클래스로 구현할 수 있는 기능 중 하나는 클래스를 정의한 이후에, 하지만 실제로 사용하기 전에 프로퍼티를 수정하거나 주석을 붙이는 것이다.** 보통 이 기법을 디스크립터와 함께 사용하여, 클래스에서 디스크립터를 어떻게 사용하는지 자세히 조사한 정보를 디스크립터에 제공한다.  

예를 들어, 고객 데이터베이스의 로우를 표현하는 새 클래스를 정의한다고 하자. 테이블의 각 칼럼(Column)에 대응하는 클래스의 프로퍼티가 있어야 한다. 따라서 프로퍼티를 칼럼 이름과 연결하는 데 사용할 디스크립터 클래스를 다음과 같이 정의한다.

```python
class Field:
    def __init__(self, name):
        self.name = name
        self.internal_name = '_' + self.name

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, '')

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)
```

_Field_ 디스크립터에 저장할 칼럼 이름이 있으면 내장 함수 _setattr_ 과 _getattr_ 을 사용해서 모든 인스턴스별 상태를 인스턴스 딕셔너리에 보호 필드로 직접 저장할 수 있다. 처음에는 이 방법이 메모리 누수를 피하려고 _weakref_ 로 디스크립터를 만드는 [방법](https://github.com/shoark7/Effective-Python/blob/master/files/BetterWay31_UseDescriptorForReusablePropertyMethod.md)보다 훨씬 편리해보인다.

```python
class Customer:
    first_name = Field('first_name')
    last_name = Field('last_name')
    prefix = Field('prefix')
    suffix = Field('suffix')
```

클래스를 사용하는 방법은 간단하다.

```python
foo = Customer()
print('Before:', repr(foo.first_name), foo.__dict__)
foo.first_name = 'Parkito'
print('After :', repr(foo.first_name), foo.__dict__)

Before: '' {}
After : 'Parkito' {'_first_name': 'Parkito'}
```

다 좋다. 잘 작동한다. 하지만 사소하지나 괘념케 하는 것이 하나 있으니, _Customer_ 클래스에서 클래스 변수로 디스크립터를 설정할 때, **각 변수의 이름을 두 번 적어야 하는 반복이 있다.** 왜 이렇게 해야만 하는 것일까?

문제는 **_Customer_ 클래스 정의에서 연산 순서가 왼쪽에서 오른쪽으로 읽는 방식과 반대라는 점이다.** 먼저 _Field_ 생성자는 *Field('first_name')* 형태로 호출한다. 다음 이 호출의 반환 값이 _Customer.field_name_ 에 할당된다. 일반적인 변수 할당과 똑같다. 그러므로 Field에서는 자신이 어떤 클래스 속성에 할당될지 미리 알 방법이 없다.


<br>

## 2. 개선: 메타클래스로 속성 이름 할당하기

중복성을 제거하려면 메타클래스를 사용하면 된다. 메타클래스를 이용하면 _class_ 문을 직접 후킹하여 _class_ 본문이 끝나자마자 원하는 동작을 처리할 수 있다.

다음 예제에서는 **필드 이름을 수동으로 여러 번 지정하지 않고 메타클래스를 사용하여 _Field.name_ 과 _Field.internal\_name_ 을 디스크립터에 자동으로 할당한다.**

```python
class Meta(type):
    def __new__(meta, name, bases, class_dict):
        for key, value in class_dict.items():
            if isinstance(value, Field):
                value.name = key
                value.internal_name = '_' + key
        cls = type.__new__(meta, name, bases, class_dict)
        return cls
```

다음은 메타클래스를 사용하는 기반 클래스를 정의한 코드다. 데이터베이스 레코드를 표현하는 클래스가 모두 이 클래스를 상속하게 해서 모두 메타클래스를 사용하게 해야 한다.

```python
class DatabaseRow(metaclass=Meta):
    pass
```

메타클래스를 사용하게 해도 필드 디스크립터는 변경이 거의 없다. 유일한 차이는 더는 생성자에 중복되는 이름 인자를 넘길 필요가 없다는 점이다. 대신 필드 디스크립터의 속성은 위의 *Meta.\_\_new\_\_* 메소드에서 설정된다.

```python
class Field:
    def __init__(self): # 인자를 직접 넘기지 않아도 된다!
        self.name = None
        self.internal_name = None

    # ... 이전과 동일
```

<br>

이제 이 모두를 활용해서 새로운 고객 데이터베이스 레코드 클래스를 만들어보자.

```python
class BetterCustomer(DatabaseRow):
    first_name = Field()
    last_name = Field()
    prefix = Field()
    suffix = Field()


foo = BetterCustomer()
print('Before:', repr(foo.first_name), foo.__dict__)
foo.first_name = 'Parkito'
print('After :', repr(foo.first_name), foo.__dict__)

Before: '' {}
After : 'Parkito' {'_first_name': 'Parkito'}
```

반복을 제거했고, 동작도 이전과 완전히 동일함을 확인할 수 있다.


<br>

## 3. 핵심 정리

* 메타클래스를 이용하면 클래스가 완전히 정의되기 전에 클래스 속성을 수정할 수 있다.
* 디스크립터와 메타클래스는 선언적 동작과 런타임 내부 조사(introspection)용으로 강력한 조합을 이룬다.
* 메타클래스와 디스크립터를 연계하여 사용하면 메모리 누수와 _weakref_ 모듈 사용을 모두 피할 수 있다.
