## Better Way 33. 메타클래스로 서브클래스를 검증하자

#### 158쪽

* Created : 2019/06/07
* Modified: 2019/06/07


<br>

## 1. 메타클래스 소개

33장부터 3장은 메타클래스에 대한 내용이다. 파이썬에서 메타클래스는 무엇인가? 내가 생각하기에 **메타클래스는 클래스를 생성할 때 호출되어 클래스에 대한 규격을 지정하고 입력에 대한 검증 등을 하는 클래스다.** 정의할 때 공통된 작업이 필요한 여러 클래스들은 한 메타클래스를 받아서 그에 맞게 자신을 정의할 수 있다.  

**메타클래스를 응용하는 가장 간단한 사례는 클래스를 올바르게 정의했는지 검증하는 것이다.** 복잡한 클래스 계층을 만들 때 스타일을 강제하거나 메소드를 오버라이드하도록 요구하거나 클래스 속성 사이에 철저한 관계를 두고 싶을 수 있다. **메타클래스는 서브클래스가 정의될 때마다 검증 코드를 실행하는 신뢰할만한 방법을 제공하므로 이럴 때 사용할 수 있다.**

보통 클래스 검증 코드는 클래스의 객체가 생성될 때 \_\_init\_\_ 메소드에서 실행된다. **하지만 메타클래스를 검증용으로 사용하면 인스턴스를 생성할 때가 아닌, 클래스를 정의할 때 바로 오류를 잡을 수 있기 때문에 문제를 더 빨리 파악할 수 있다.**

<br>

이에 대해 바로 살펴보기 전에 먼저 메타클래스를 정의하는 방법을 살펴보자.

**메타클래스는 _type_ 을 상속하여 정의하며, 자체의 \_\_new\_\_ 메소드에서 생성되고 있는 클래스의 정보를 여러 개 받는다.** 클래스를 정의할 때 받는 이 정보들을 통해 클래스를 검증하는 등의 작업을 할 수 있다. 매우 간단한 메타클래스를 코드로 정의해보자.

```python
class Meta(type):
    def __new__(meta, name, bases, class_dict):
        print("New method from Meta called! And I have followings:")
        print("  meta: ", meta)
        print("  name: ", name)
        print("  bases: ", bases)
        print("  class_dict: ", class_dict)
        return type.__new__(meta, name, bases, class_dict)

class MyClass(metaclass=Meta):
    cls_var = 123

    def foo(self):
        pass


New method from Meta called! And I have followings:
  meta:  <class '__main__.Meta'>
  name:  MyClass
  bases:  ()
  class_dict:  {'__module__': '__main__', '__qualname__': 'MyClass', 'cls_var': 123, 'foo': <function MyClass.foo at 0x7f848c842c80>}
```

먼저 메타클래스 _Meta_ 를 정의했다. _type_ 클래스를 상속받고 자체의 \_\_new\_\_ 메소드를 구현하고 있다. 이 메소드는 4개의 인자를 받는데 각 값을 확인하기 위해 print로 값을 출력한다. 출력 후에는 원형 메타클래스의 \_\_new\_\_ 를 호출해서 클래스 정의를 마친다.

다음은 _Meta_ 를 메타클래스로 하는 _MyClass_ 클래스를 정의했다. **메타클래스 선언은 클래스 이름 옆 `()` 괄호에 'metaclass' 인자로 지정한다.** 이 클래스는 클래스 변수와 메소드 하나를 정의했다.

재밌는 것은 다음에 출력된 화면이다. _Meta_ 에서 화면에 출력한 변수들의 값이 나오는데 이들을 설명하면 다음과 같다.

* **meta: 메타클래스 자신을 말한다. 메소드에서 _self_, 클래스메소드에서 _cls_ 를 지칭하는 것과 같다.**
* **name: 클래스 자신의 이름을 말한다. 여기서는 _MyClass_**
* **bases: 클래스가 상속받은 부모클래스들을 말한다. 여기서는 상속받지 않았기 때문에 빈 튜플이 나왔다.**
* **class\_dict: 클래스가 정의한, 클래스가 가지게 될, 즉 clss.\_\_dict\_\_에 담기게 될 속성을 담은 _dict_이다. 여기서는 클래스 변수 _cls\_var_ 와 메소드 _foo_ 가 담겨 있다.**


이때 기억할 것은 **저 출력문들은 인스턴스 생성할 때가 아닌, 클래스 정의 코드를 실행했을 때 출력됐다는 점이다.** 클래스가 정의될 때 메타클래스의 \_\_new\_\_ 메소드가 같이 실행되며 이 메소드가 무사히 마쳐야 클래스도 문제없이 정의되었다고 할 수 있다.


<br>

## 2. 메타클래스 사용 예제: 클래스 검증하기

이제 실제로 메타클래스를 유용한 작업에 사용해보자. 앞서 이야기한 '클래스가 올바르게 정의됐는지 검증하는 작업'을 해볼 예정이다.  

예를 들어 2차원 다각형을 클래스로 구현한다고 하자. 모든 다각형의 변의 수는 최소 3이다. 즉 그 이하의 변을 정의하는 다각형 클래스는 튕겨내야 하는 것이다. **이렇게 하려면 특별한 검증용 메타클래스를 정의한 후 다각형 클래스 계층의 기반 클래스에 사용하면 된다.**

이때 명심할 것은 다각형들의 기반이 되는 추상 다각형에는 검증을 적용하지 말아야 한다. 그 이유에는 일반적으로 **추상 다각형에서는 속성에 _None_ 과 같은 정의되지 않은 값을 설정하기 때문이다.**

```python
class ValidatePolygon(type):
    def __new__(meta, name, bases, class_dict):
        if bases != ():
            if class_dict['sides'] < 3:
                raise ValueError("Polygon needs 3+ sides")

        return type.__new__(meta, name, bases, class_dict)

class AbstractPolygon(metaclass=ValidatePolygon):
    sides = None

    @classmethod
    def sum_interior_angles(cls):
        return 180 * (cls.sides - 2)

class Triangle(AbstractPolygon):
    sides = 3
```

위 내용을 구현한 세 개의 클래스를 선언했다. 이때의 계층구조를 먼저 간략하게 설명하고 각 클래스를 살펴보자.

* _ValidatePolygon_ : 다각형 생성 시 면의 개수가 반드시 3이상이 되도록 검증할 메타클래스이다.
* _AbstractPolygon_ : 다른 모든 다각형의 추상이 되는 추상클래스다. 이 추상클래스를 상속받아 삼각형, 사각형, N각형이 정의된다.
* _Triangle_ : 추상다각형 클래스를 상속받아 만든 삼각형 클래스다.


<br>

이제 각 함수를 살펴보도록 하자.

```python
class ValidatePolygon(type):
    def __new__(meta, name, bases, class_dict):
        if bases != ():
            if class_dict['sides'] < 3:
                raise ValueError("Polygon needs 3+ sides")

        return type.__new__(meta, name, bases, class_dict)
```

다각형 클래스를 검증할 메타클래스를 선언했다. 이 클래스가 하는 일은 간단하다. 모든 2차원 다각형은 최소 3개 이상의 변을 가져야 하기 때문에 3개 미만의 변을 가지게 되면 _ValueError_ 을 일으킨다. 이때 변의 개수를 확인할 때 *class\_dict* 를 사용한다. 이 딕셔너리는 클래스에 정의된 메소드, 클래스 변수를 담고 있기에 여기서 `sides` 속성을 찾아 그 값을 검증하고 있다. validation을 통과하면 문제가 없기에 끝낸다.

중요한 것은 **_bases_, 즉 부모클래스 튜플이 비어있다면 검증절차를 거치지 않는다는 것이다.** 정의한 클래스 계층 구조에서 부모클래스 튜플이 비어있을 경우는 클래스가 추상클래스일 때다. 이때는 구체적인 변의 개수를 지정하지 않는다.(`추상`의 의미는 '구체성이 없다'와 일치하니까)


```python
class AbstractPolygon(metaclass=ValidatePolygon):
    sides = None

    @classmethod
    def sum_interior_angles(cls):
        return 180 * (cls.sides - 2)
```

추상다각형 클래스를 정의했다. 메타클래스로 _ValidatePolygon_ 클래스를 받고 있음을 확인할 수 있다. 강조했듯이 _sides_ 는 _None_ 으로 정의한다. 클래스메소드로 다각형의 내각의 함을 계산하는 함수를 미리 만들어놓았다. 저 식은 초등학교에서 배웠던 것으로 기억한다.


```python
class Triangle(AbstractPolygon):
    sides = 3
```

추상다각형 크래스를 상속받은 삼각형 클래스를 선언했다. 삼각형에 맞게 _sides_ 를 3으로 설정한 것을 알 수 있다.

테스트해보면 잘 작동한다.

```python
print(Triangle.sum_interior_angles())

180
```

<br>

포스트를 마무리하기 전에 메타클래스 \_\_new\_\_의 간단한 다른 특징을 살펴본다. 바로 **클래스 생성 시에 \_\_new\_\_ 메소드의 호출 순서**에 관한 내용이다. 클래스가 생성될 때 다른 내용들이 실행되기 전에 이 메소드가 먼저 호출될까, 중간에 호출될까, 아니면 정의를 마치면서 마지막에 실행될까? 매우 간단한 예제로 확인하면 되겠다.

```python
print('Start')
class Line(AbstractPolygon):
    print('Line class definition starts')
    sides = 1
    print('Line class definition ends')
print('Ended!')


Start
Line class definition starts
Line class definition ends

ValueError: Polygon needs 3+ sides
```

선분 클래스를 정의했다. 선분 자체가 곧 변의 개수가 1이기 때문에 \_\_new\_\_ 메소드에서 _ValueError_ 가 반환될 것은 당연하다. 중요한 것은 순서인데 print문을 통해 확인할 수 있다.

에러가 출력되기 전 마지막 문장이 클래스 선언 후이다. 즉 **클래스 선언의 다른 코드들이 다 실행된 후에 \_\_new\_\_ 메소드가 실행되는 것.**

<br>


## 3. 핵심 정리

* 서브클래스 타입의 객체를 생성하기에 앞서 서브클래스가 정의 시점부터 제대로 구성되었음을 보장하려면 메타클래스를 사용하자.
* 메타클래스의 \_\_new\_\_ 메소드는 class 문의 본문 전체가 처리된 후에 실행된다.
