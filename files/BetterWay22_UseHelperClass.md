## Better Way 22. 딕셔너리와 튜플보다는 헬퍼 클래스로 관리하자

#### 90쪽

* Created : 2016/10/30
* Modified: 2019/05/21  

<Br>

## 1. 기본 자료구조를 사용한 데이터 구조화와 문제점

**파이썬에 내장되어 있는 딕셔너리 타입은 객체의 수명이 지속되는 동안 동적인 내부상태를 관리하는 용도로 아주 좋다.  '동적'의 의미는 예상하지 못한 식별자를 관리해야 하는 상황을 말한다.**

예를 들어 이름을 모르는 학생 집단의 성적을 관리하고 싶다고 해보자. 학생별로 딕셔너리에 이름을 지정하는 성적표 클래스를 정의할 수 있다.


```python
class SimpleGradebook:
    def __init__(self):
        self._grades = {}

    def add_student(self, name):
        self._grades[name] = []

    def report_grade(self, name, score):
        self._grades[name].append(score)

    def average_grade(self, name):
        grades = self._grades[name]
        if not len(grades):
            raise ValueError("입력된 성적이 없습니다")
        return sum(grades) / len(grades)
```

객체지향에 대한 최소한의 이해가 있으면 무난하게 짤 수 있는 클래스다. 반별로 성적표 클래스를 만들어 내부 딕셔너리를 둔 뒤에 각 원소로 학생들의 이름을 key에, 그들의 성적을 기록하는 리스트를 value로 담는다. 클래스를 사용하는 방법은 간단하다.

```python
book = SimpleGradebook()
book.add_student('Park Sunghwan')
book.report_grade('Park Sunghwan', 80)

>>> print(book.average_grade('Park Sunghwan'))

80.0
```

<br>

**딕셔너리는 사용하기 정말 쉬워서 과도하게 쓰다가 코드를 취약하게 만들기 쉽다.** 예를 들어, SimpleGradebook을 확장해서 모든 성적을 한 곳에 관리하지 않고, 과목별로 저장한다고 해보자. 이런 경우 _self.\_grades_ 를 변경해서 **학생 이름(키)에 리스트가 아닌 또 다른 딕셔너리를 매핑할 수 있다.** 딕셔너리 안에 딕셔너리가 들어가는 형태로 가장 안쪽 딕셔너리는 과목에 성적을 매핑한다.

```python
class BySubjectGradebook:
    def __init__(self):
        # 전체 자료를 담을 딕셔너리 정의
        self._grades = {}

    def add_student(self, name):
        # 딕셔너리 안 학생 정보를 담을 딕셔너리를 또 생성
        self._grades[name] = {}

    def report_grade(self, name, subject, grade):
        # 학생 딕셔너리 안에 과목 리스트를 생성하고 점수 입력
        by_subject = self._grades[name]
        grade_list = by_subject.setdefault(subject, [])
        grade_list.append(grade)

    def average_grade(self, name):
        # 한 학생의 모든 과목의 모든 점수를 합산하여 평균을 구함.
        by_subject = self._grades[name]
        total, count = 0, 0
        for grades in by_subject.values():
            total += sum(grades)
            count += len(grades)
        return total / count
```

```python
# 성적부 예시를 JSON 형태로 구조화했음
BySubjectGradebook = {
	grades = {
		'박성환' : {
			'수학': [100, 20, 40],
			'국어': [80,20, 40],
			'영어': [80, 20, 40],
		}
		'동에번쩍' : {
			'수학': [39, 21, 80],
			'국어': [80,25, 100],
			'영어': [82, 90, 91],
		}
	
	}
}
```


해당 코드는 아직까지는 다룰만해 보인다.

```python
book = BySubjectGradebook()
book.add_student('stonehead')
book.report_grade('stonehead', 'math', 75)
book.report_grade('stonehead', 'math', 65)
book.report_grade('stonehead', 'gym', 90)
book.report_grade('stonehead', 'gym', 90)
```

<br>

더 깊숙히 들어가보자. 요구사항이 바껴서 **수업의 최종성적에서 각 점수가 차지하는 가중치를 매겨서 중간고사와 기말고사를 쪽지시험보다 중요하게 만들려고 한다.** 이 기능을 구현하는 방법 중 하나는 가장 안쪽 딕셔너리를 변경해서 과목(키)을 성적(값)에 매핑하지 않고, 성적과 비중을 담은 튜플(score, weight)에 매핑하는 것이다. 지금부터 뭔가 아득해진다.

```python
class WeightedGradebook:
    # 생략 ...
    def report_grade(self, name, subject, score, weight):
        by_subject = self._grades[name]
        grade_list = by_subject.setdefault(subject, [])
        grade_list.append(score, weight)

    def average_grade(self, name):
        by_subject = self._grades[name]
        score_sum, score_count = 0, 0
        for subject, socres in by_subject.items():
            subject_avg, total_weight = 0, 0
            for score, weight in scores:
                # ...
        return score_sum / score_count
```

**`average_grade`의 함수 활용이 반복문의 중첩으로 이해하기 어려워졌을 뿐만 아니라,`book.report_grade('stonehead', 'math', 80, 0.2)`와 같이 함수 호출에서도 인자가 무엇을 의미하는지 명확하지도 않다.**  

**이 정도로 복잡해지면 딕셔너리와 튜플 대신 클래스의 계층 구조를 사용할 때가 된 것이다.** 처음에야 단순한 성적표 클래스를 구현하려 했으니 복잡하게 헬퍼클래스를 추가할 필요까지는 없었을 것이다. 그렇지만 결과적으로는 요구 복잡도가 증가했으며, 이때 경험칙으로서 **딕셔너리와 튜플을 사용해서 중첩이 한 단계 넘게 활용하지 말아야 한다.** 인간은 2차원이 넘어가는 구조는 직관적으로 이해하기 힘들어하기 때문이다.

여러 계층으로 중첩하면 다른 프로그래머들이 코드를 이해하기 힘들고, 유지보수가 극도로 어려워진다. **이처럼 관리가 복잡하다고 느끼는 즉시 클래스로 옮겨가야 한다. 그러면 데이터를 더 잘 캡슐화한, 잘 정의된 인터페이스를 제공할 수 있다.**


<br>

## 2. 클래스 리펙토링

**의존관계에서 가장 아래에 있는 성적부터 클래스로 옮겨보자.** 그러나 이렇게 간단한 정보를 담기에 클래스는 너무 무거워 보인다. 성적은 변하지 않으니 튜플을 사용한다.

```python
grades = []
grades.append((95, 0.4))

# ...
total = sum(score * weight for score, weight in grades)
total_weight = sum(weight for _, weight in grades) 
# 파이썬에서는 반복문 등에서 사용하지 않을 변수를 관례적으로 '_'으로 표현한다.
average_grade = total / total_weight
```

이는 간단하지만 문제는 일반 튜플은 위치에 의존한다는 점이다. 성적에 선생님의 의견같은 더 많은 정보를 연관 지으려면 튜플을 사용하는 곳 모두에 아이템을 두 개가 아니라 세 개를 추가해야 한다.

```python
grades = []
grades.append((94, 0.2, 'Great!!'))
```

튜플을 점점 더 길게 확장하는 패턴은 딕셔너리의 계층을 깊게 두는 방식과 비슷하다. **튜플의 아이템이 두 개를 넘어가면 다른 방법을 고려해야 한다.**

이 때 `collections` 모듈의 [namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple)이 정확히 이런 요구에 부합한다. `namedtuple`을 이용하면 작은 불변 데이터 클래스를 쉽게 정의할 수 있다.

```python
import collections

Grade = collections.namedtuple('Grade', ('score', 'weight'))
```

불변 데이터 클래스는 위치 인수나 키워드 인수로 생성할 수 있다. 그리고 **일반 튜플이 원소에 정수 인덱스로 접근하는 것과 달리 문자열 이름을 속성으로 접근할 수 있다.** 이름이 붙은 속성이 있으면 나중에 요구사항이 또 변해서 단순 데이터 컨테이너에 동작을 추가해야 할 때 용이하다.  
  
`namedtuple`을 직접 사용해서 코드를 작성해보자. 한 학생이 공부한 과목들을 표현하는 클래스를 작성하자.

```python
class Subject:
    def __init__(self):
        self._grades = []

    def report_grade(self, score, weight):
        self._grades.append(Grade(score, weight))

    def average_grade(self):
        total, total_weight = 0, 0
        for grade in self._grades:
            total += grade.score * grade.weight
	    # 튜플에 인덱스가 아닌 키워드로 접근했다.
            # 이게 namedtuple의 장점. 숫자는 언제나 문제보다 이해가 어렵다.
            total_weight += grade.weight
        return total / total_weight
```

다음은 학생 한 명을 관리하는 클래스를 만들자. 이 클래스는 앞서 정의한 _Subject_ 클래스를 사용할 것이다.


```python
class Student:
    def __init__(self):
        self._subjects = {}

    def subject(self, name):
        return self._subjects.setdefault(name, Subject())

    def average_grade(self):
        total, count = 0, 0
        for subject in self._subjects.values():
            total += subject.average_grade()
            count += 1
        return total / count
```

마지막으로 학생의 이름을 키로 사용해 동적으로 모든 학생을 담을 성적표 클래스를 작성한다.

```python
class Gradebook(object):
    def __init__(self):
        self._students = {}

    def student(self, name):
        if name not in self._students:
            self._students[name] = Student()
        return self._students[name]
```

**이 세 클래스의 총 코드 줄 수는 이전에 구현한 코드의 두 배에 가깝다. 하지만, 이 코드가 훨씬 이해하기 쉽다. 예제도 더 명확하고 확장하기도 쉽다.**

```python
book = Gradebook()
albert = book.student('albert')
math = albert.subject('math')
math.report_grade(80, 0.1)

# ...
print(albert.average_grade())
```

이렇게 **복잡도가 2차원을 상회하게 되면 단순 _dict_ 같은 자료구조 사용을 지양해야 하며 각 차원 단위를 클래스로 관리하는 것을 심각하게 고려해야 한다.**


<br>

## 3. 핵심 정리

* 다른 딕셔너리나 긴 튜플을 값으로 담은 딕셔너리를 생성하지 말자.
* 정식 클래스의 유연성이 필요없다면 가벼운 불변 데이터 컨테이너에는 `namedtuple`을 사용해보자.
* 내부상태를 관리하는 딕셔너리가 복잡해지면 여러 헬퍼 클래스를 사용하는 방식으로 코드를 관리하자.
