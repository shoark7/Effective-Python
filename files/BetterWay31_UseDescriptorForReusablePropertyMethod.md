## Better Way 31. 재사용 가능한 @property 메소드에서는 디스크립터를 사용하자

#### 144쪽

* Created : 2019/06/05
* Modified: 2019/06/05

<br>


## 1. @property의 한계

이전 장들에서 속성 평가와 할당에 간단한 추가적인 동작을 넣거나, 속성을 동적으로 계산하는 데 @property와 setter가 유용함을 확인했다.  

하지만 **@property와 setter에 가장 큰 한계는 `재사용성`이다.** 다시 말해 @property와 setter로 데코레이트하는 메소드를 같은 클래스에 속한 여러 속성에 사용하지 못한다. 또 관련 없는 클래스에서도 재사용할 수 없다.

그 한계를 확인하는 예제를 만들어보자. 파이썬 클래스를 만드는데 학생들을 위해 매일매일의 숙제에 해당하는 클래스 _Homework_ 를 만들어보자.

```python
class Homework:
    def __init__(self):
        self._grade = 0

    @property
    def grade(self):
        return self._grade

    @grade.setter
    def grade(self, value):
        if not (0 <= value <= 100):
            raise ValueError("시험 점수는 0 이상, 100 이하만 가능합니다")
        self._grade = value
```

매우 친숙한 @property와 setter의 활용 예제다. 이 예제는 grade라는 속성을 동적으로 검증하고 할당하고 확인한다.


```python
park = Homework()
park.grade = 95
```

여긴 맛보기다. 이제는 숙제가 아닌 학생들의 시험 성적을 매긴다고 해보자. 시험은 여러 과목으로 구성되어 있고, 과목별로 점수가 있다.


```python
class Exam:
    def __init__(self):
        self._writing_grade = 0
        self._math_grade = 0

    @staticmethod
    def _check_grade(value):
        if not (0 <= value <= 100):
            raise ValueError("시험 점수는 0 이상, 100 이하만 가능합니다")
```

여러 과목의 점수를 보호 속성으로 먼저 할당한다. 과목의 점수를 입력할 때 입력값에 대한 검증이 각각 필요하기 때문에 이를 위해 입력 점수를 검증하는 staticmethod를 할당한다. 이 메소드는 각 과목의 점수 할당 setter 메소드에서 사용할 것이다.


벌써 이 정도만 해도 감을 잡을 수 있을 것이다. **동적으로 관리해야 여러 개라면 그때마다 @property와 setter를 작성해야 해서 금방 코드가 장황해진다.** 두 속성에 대한 프로퍼티 메소드를 마저 정의하면 다음과 같다.

```python
    @property
    def writing_grade(self):
        return self._writing_grade

    @grade.setter
    def writing_grade(self, value):
        self._check_grade(value)
        self._writing_grade = value

    @property
    def math_grade(self):
        return self._math_grade

    @grade.setter
    def math_grade(self, value):
        self._check_grade(value)
        self._math_grade = value
```

이런 방법은 범용으로 사용하기에도 좋지 않다. 관리해야 하는 상태의 개수는 시스템의 복잡도가 증가할수록 배가되는데 각 상태마다 @property와 setter를 작성하는 일은 매우 성가실 것이다.

<br>

## 2. 해결책: descriptor 사용하기

파이썬에서 이런 작업을 할 때 더 좋은 방법은 descriptor(이하 "디스크립터")를 사용하는 것이다. **디스크립터 프로토콜(descriptor protocol)은 속성에 대한 접근을 언어에서 해석할 방법을 정의한다.** 이전에 이터레이터 프로토콜(Iterator Protocol)을 기억하는지? 이 프로토콜을 준수하는 객체를 만들면 객체를 반복문 등에서 순회할 수 있었다. 디스크립터 프로토콜도 이와 마찬가지로 이 프로토콜을 준수하는 객체를 만들면 객체에서 속성에 접근하고 할당하는 로직을 커스텀화할 수 있다.

**프로토콜에서 디스크립터 클래스는 반복코드 없이도 성적 검증 동작을 재사용화할 수 있게 해주는 \_\_get\_\_, \_\_set\_\_ 메소드를 제공할 수 있다.** 이터레이터 프로토콜에서 \_\_next\_\_, \_\_iter\_\_ 등의 메소드를 구현한 것과 마찬가지의 논리다. 디스크립터를 이용하면 한 클래스의 서로 다른 많은 속성에 같은 로직을 재사용할 수 있다.

<br>

이번에는 Grade 인스턴스를 `클래스 속성`으로 포함하는 새로운 Exam 클래스를 정의한다. Grade 클래스는 디스크립터 프로토콜을 구현한다. Grade 클래스의 동작 원리를 설명하기 전에 코드에서 Exam 인스턴스에 있는 이런 디스크립터 속성에 접근할 때 파이썬이 무슨 일을 하는지 이해해야 한다.

```python
class Grade:
    def __get__(*args, **kwargs):
        # ...

    def __set__(*args, **kwargs):
        # ...


class Exam:
    math_grade = Grade()
    writing_grade = Grade()
    science_grade = Grade()
```

디스크립터 활용의 기본 뼈대만 대충 구현했기 때문에 구체적인 코드는 아직 적지 않았다. 일단 구조만 먼저 보자. _Grade_ **클래스는 \_\_get\_\_, \_\_set\_\_ 메소드를 구현한 디스크립터 클래스고, _Exam_ 클래스는 각 과목을 _Grade_ 인스턴스로 두고 있다. 이때 _Exam_ 의 속성은 인스턴스 속성이 아닌 클래스 속성으로 둔 것을 눈여겨 보자.**

그리고 다음과 같이 속성을 할당하자.

```python
exam = Exam()
exam.writing_grade = 40
```

글쓰기 성적을 40으로 할당했다. 저 성적은 디스크립터 인스턴스이고, 이때 저 할당식은 내부적으로는 다음과 같이 해석된다.

```python
Exam.__dict__['writing_grade'].__set__(exam, 40)
```

이번에는 할당 대신 값을 얻어온다고 하자

```python
Exam.__dict__['writing_grade'].__get__(exam, Exam)
```

이렇게 동작하게 만드는 건 객체의 \_\_getattribute\_\_ 메소드다. 간단히 말하면 **Exam `인스턴스`에 _writing\_grade_ 속성이 없으면 파이썬은 대신 `클래스` 속성을 이용한다. 이 클래스의 속성이 \_\_get\_\_, \_\_set\_\_ 메소드를 갖춘 객체라면 파이썬은 디스크립터 프로토콜을 따른다고 가정한다.**

<br>

이 디스크립터를 사용해서 재사용 가능한 속성 동작을 제공해보자. 먼저 첫 번째 시도다.

```python
class Grade:
    def __init__(self):
        self._value = 0

    def __get__(self, instance, instance_type):
        return self._value

    def __set__(self, instance, value):
        if not (0 <= value <= 100):
            raise ValueError("시험 점수는 0 이상, 100 이하만 가능합니다")
        self._value = value
```

* **_Grade_ 클래스를 \_\_get\_\_, \_\_set\_\_ 메소드를 구현함으로써 디스크립터 클래스로 만들었다.** 이때 두 메소드의 인자는 프로토콜에서 명시하는 대로 정의해줘야 한다.
* \_\_set\_\_ 메소드는 점수의 범위를 검증하는 로직이 들어있다. 이제 _Grade_ 인스턴스를 속성으로 쓰는 클래스는 속성을 일일이 검증하지 않아도 된다.

불행히도 이 코드는 예상한 대로 동작하지는 않을텐데, 테스트해보자. 한 Exam 인스턴스를 대상으로는 잘 작동한다.


```python
first_exam = Exam()
first_exam.writing_grade = 82
first_exam.science_grade = 99

Writing score is 82
Science score is 99
```

문제가 있나 싶은데 한 개가 아닌 여러 인스턴스를 생성해서 속성에 접근하면 기대하지 않은 동작을 하게 된다.


```python
second_exam = Exam()
second_exam.writing_grade = 75

print('Frist writing score is', first_exam.writing_grade)
print('Second writing score is', second_exam.writing_grade)


Frist writing score is 75
Second writing score is 75
```

뭔가 이상하다. 첫 시험에서 쓰기 성적은 82점으로 할당했는데 두 번째 시험을 보고 나서 점수가 일치하게 됐다. 사실 이런 결과가 나온 이유는 명확하다. **_Exam_ 클래스에서 _writing\_grade_ 는 클래스 변수로 할당했다.** 따라서 한 인스턴스에서 속성을 변경하면 클래스 변수는 모든 인스턴스에 적용되기 때문에 첫 번째 시험의 속성값도 변한 것으로 출력되는 것이다.


<br>

이 문제를 해결하려면 각 Exam 인스턴스별로 값을 추적하는 Grade 클래스가 필요하다는 것은 자명하다. 여기서는 딕셔너리에 각 인스턴스의 상태를 저장하는 방법을 값을 추적한다.

```python
class Grade:
    def __init__(self):
        self._values = {}

    def __get__(self, instance, instance_type):
        if instance is None:
            return self

        return self._values.get(instance, 0)

    def __set__(self, instance, value):
        if not (0 <= value <= 100):
            raise ValueError("시험 점수는 0 이상, 100 이하만 가능합니다")
        self._values[instance] = value
```

Grade를 재정의했다. 아까의 **Grade와 달리 *\_values* 변수를 _dict_ 로 둠으로써 _Exam_ 객체마다 키로 두고 그에 맞는 성적값을 불러올 수 있다. 즉, 클래스가 아닌 인스턴스별로 속성값을 추적할 수 있게 된 것이다.**



## 3. descriptor 예제 개선

위의 구현은 간단하면서도 잘 동작하지만 여전히 문제점이 하나 남아 있다. 바로 메모리 누수다.(memory leak) _\_value_ 딕셔너리는 프로그램의 수명 동안 \_|_set|_\_에 전달된 모든 Exam 인스턴스의 참조를 저장한다. **결국 각 인스턴스의 참조의 개수가 절대로 0이 되지 않아 가비지 컬렉터가 정리되지 못하게 된다.**  

이런 참조 관련 문제는 내장 **_weakref_ 모듈**을 사용해 해결할 수 있다. 이 모듈은 _\_values_ 에 사용한 간단한 딕셔너리를 대체할 수 있는 WeakKeyDictionary 라는 특별한 클래스를 제공한다. **이 클래스의 주요 특징은 런타임 도중 가지고 있는 키에 대한 참조가 마지막이라는 것을 알면 키 집합에서 Exam 인스턴스를 제거한다.** 파이썬이 대신 참조를 관리해주고 모든 Exam 인스턴스가 더는 사용되지 않으면 딕셔너리가 비어 있게 한다.

```python
from weakref import WeakKeyDictionary

class Grade:
    def __init__(self):
        self._values = WeakKeyDictionary()
	# ...
```

아까의 예제에서 _\_values_ 만 기본 딕셔너리에서 _WeakKeyDictionary_ 로 교체했다. 다음과 같은 Grade 디스크립터 구현은 모두 기대한 대로 동작한다.


```python
from weakref import WeakKeyDictionary

class Grade:
    def __init__(self):
        self._values = WeakKeyDictionary()

    def __get__(self, instance, instance_type):
        if instance is None:
            return self

        return self._values.get(instance, 0)

    def __set__(self, instance, value):
        if not (0 <= value <= 100):
            raise ValueError("시험 점수는 0 이상, 100 이하만 가능합니다")
        self._values[instance] = value

class Exam:
    math_grade = Grade()
    writing_grade = Grade()
    science_grade = Grade()


first_exam = Exam()
first_exam.writing_grade = 82
second_exam = Exam()
second_exam.writing_grade = 75

print('Frist writing score is', first_exam.writing_grade)
print('Second writing score is', second_exam.writing_grade)


Frist writing score is 82
Second writing score is 75
```

이번에는 아까와 달리 인스턴스별로 정보가 관리되는 것을 확인할 수 있고 메모리 누수 또한 발생하지 않을 것이라 예상할 수 있다.


<br>

## 4. 핵심 정리

* 직접 디스크립터 클래스를 정의하여 @property 메소드의 동작과 검증을 재사용하자.
* WeakKeyDictionary를 사용하여 디스크립터 클래스가 메모리 누수를 일으키지 않게 하자.
* \_\_getattribute\_\_가 디스크립터 프로토콜을 사용하여 속성을 얻어오고 설정하는 원리를 정확히 이해하려는 함정에 빠지지 말자.
