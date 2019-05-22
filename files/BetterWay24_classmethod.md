## Better Way 24. 객체를 범용으로 생성하려면 @classmethod 다형성을 이용하자

#### 102쪽

* Created : 2017/04/27
* Modified: 2019/05/22  

<br>

## 1. 클래스에서의 다형성

객체 지향 패러다임에서 `다형성`(polymorphism)은 핵심적인 개념 중 하나이다. 다형성은 쉽게 말해 하나의 정의가 여러 개의 형태를 가질 수 있다는 것인데 이해가 안 되면 주위를 둘러보라. 같은 인간 종에 속하되, 천차만별의 다양성을 지닌 사람들을 볼 수 있다. 하지만 이들은 모두 인간으로, 인간종의 핵심적인 특징들을 공유하고 있다. 이게 곧 다형성이다.  

**파이썬은 다른 객체 지향 언어들과 달리 인스턴스가 다형성을 지원할 뿐만 아니라, 클래스 자체도 다형성을 잘 지원한다.** 이게 무슨 의미이고 어떤 장점이 있겠는가?

**클래스에서의 다형성은 상속계층 구조에 속한 여러 클래스가 자체의 메소드를 독립적인 버전으로 구현하는 방식이다.** 다형성을 이용하면 여러 클래스가 같은 인터페이스나 추상 기반 클래스를 충족하면서도 다른 기능을 제공할 수 있다.

이번 예제에서는 Mapreduce(이하 "맵리듀스") 구현을 통해 살펴보자. 맵리듀스는 대량의 데이터를 부분마다 병렬적으로 로드해서 전처리한 뒤(map), 하나의 값으로 환원(reduce)하는 두 과정을 합친 프로그래밍 모델을 이야기한다. 


<br>

## 2. 일반 클래스 구현의 맹점

먼저 맵리듀스는 처리할 데이터를 로드해야 한다. 입력 데이터는 여러 형태가 있을 수 있기 때문에 일반 추상적인 클래스를 정의하고 이후에 필요에 따라 서브 클래스들이 각 입력 방법을 정의한다고 하자. 추상 입력 데이터 클래스는 다음과 같다.

```python
class InputData:
    def read(self):
        raise NotImplementedError
```

일반적으로 추상 클래스는 향후 지원할 행동과 속성을 정의만하고 구체적인 명세는 하지 않는다. 추상적이고 눈에 보이지 않는 대상의 구체적인 행동이나 속성을 어떻게 명시적으로 정의하겠는가? 그래서 데이터를 읽는 필수적인 메소드 _read_ 가 구현되지 않았다는 뜻의 _NotImplementedError_ 에러를 반환한다.

이제 이 추상 클래스를 상속해 디스크에서 경로 파일의 데이터를 읽어오는 서브클래스를 만들자.

```python
class PathInputData(InputData):
    def __init__(self, pat):
        super().__init__()
        self.path = path

    def read(self):
        return open(self.path).read()
```

이 클래스는 디스크의 파일을 읽었지만 다른 서브클래스들은 네트워크에서 데이터를 읽거나, 데이터의 압축을 해체하는 기능 등 다양한 변형을 만들 수 있다. 하지만 모든 서브클래스는 단일 추상 클래스를 상속하기 때문에 데이터를 로드하는 _read_ 메소드는 가지고 있을 것이다. 인간이 다 다르지만 인간종의 핵심적인 특징은 공유하는 것과 마찬가지다.

<br>


이제는 입력된 데이터를 처리하는 맵리듀스 작업 클래스에도 비슷한 추상 인터페이스를 만들자.


```python
class Worker:
    def __init__(self, input_data):
        self.input_data = input_data
        self.result = None

    def map(self):
        raise NotImplementedError

    def reduce(self, other):
        raise NotImplementedError
```

이 추상 클래스를 상속하는 구체적인 서브클래스를 구현할텐데 쉬운 예제로 모든 데이터의 전체 줄수를 계산하는 카운터를 만든다고 하자.

```python
def LineCountWorker(Worker):
    def map(self):
        data = self.input_data.read()
        self.result = data.count('\n')

    def reduce(self, other):
        self.result += other.result
```

클래스들 자체는 문제가 없어보인다. 하지만 이내 커다란 문제에 직면하는데, **이 모든 코드 조각(클래스들)을 어떻게, 무엇으로 연결할 것인가?** 적절히 인터페이스를 설계하고 추상화한 클래스들이지만, 일단 객체를 생성한 후에나 유용하다. 무엇으로 객체를 만들고 맵리듀스를 조율할까?


<br>

## 3. 해결책 1: 헬퍼 함수를 만들어 객체를 만들어 연결하기

이 클래스들을 활용하는 가장 무난한 방법은 이들을 연결하는 글루 코드를 헬퍼 함수로 작성하는 것이다. 다음은 디렉토리의 내용을 나열하고 그 안에 있는 각 파일로 _PathInputData_ 인스턴스를 생성하는 코드다.

```python
import os

def generate_inputs(data_dir):
    for name in os.listdir(data_dir):
        yield PathInputData(os.path.join(data_dir, name))
```

다음으로 _generate\_inputs_ 함수에서 반환한 _InputData_ 인스턴스를 사용하는 _LineCountWorker_ 인스턴스를 생성한다.

```python
def create_workers(input_list):
    workers = []
    for data in input_list:
        workers.append(LineCountWorker(data))
    return workers
```

map 단계를 여러 스레드로 나눠서 이 Worker 인스턴스들을 실행한다. 그런 다음 reduce를 반복적으로 호출해서 결과를 최종값 하나로 합친다.


```python
def execute(workers):
    threads = [Thread(target=w.map) for w in workers]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

    first, *rest = workers
    for worker in rest:
        first.reduce(worker)

    return first.result
```

마지막으로 단계별로 실행하는 템플릿 메소드인 mapreduce 함수에서 모든 조각을 연결한다.

```python
def mapreduce(data_dir):
    inputs = generate_inputs(data_dir)
    workers = create_workers(inputs)
    return execute(workers)
```

테스트용 입력 파일로 이 함수를 실행해보면 잘 동작한다.


```python
from tempfile import TemporaryDirectory

def write_test_files(tmpdir):
    #...


with TemporaryDirectory() as tmpdir:
    write_test_files(tmpdir)
    result = mapreduce(tmpdir)

print('There are', result, 'lines')


There are 4360 lines
```

이 코드는 어떻게 생각하는가? 각 부분기능을 잘 나누고 구현했다고는 생각이 든다. 하지만 이 코드는 치명적인 약점이 있는데, 재사용성이 매우 안 좋다는 것이다. 앞서 데이터를 로드하는 기능은 디스크에서 파일을 읽는 방법뿐 아니라, 네트워크, 압축 해체 등의 기능을 제공하는 다른 서브클래스들로도 구현할 수 있다고 했다. 이런 다형성은 워커도 마찬가지다. 지금은 줄수를 세는 것만 하지만 나중에는 더 원대한 작업을 할 수도 있다.  

**하지만 현재는 다른 InputData나 Worker 서브클래스를 작성한다면 _generate\_inputs_, _create\_workers_, _mapreduce_ 를 그에 알맞게 다시 작성해야 한다. 즉, 재사용성이 구리다.**

이 문제는 결국 객체를 생성하는 범용적인 방법의 필요성으로 귀결된다. 다른 언어에서는 이 문제를 생성자 다형성으로 해결한다. 하지만 파이썬에서는 단일 생성자(\_\_init\_\_)만을 허용한다.

이럴 때 클래스 다형성을 이용하는 방법을 추천할만하다.


<br>

## 4. 해결책 2: @classmethod 다형성 사용하기

이 문제를 해결하는 가장 좋은 방법은 `@classmethod` 다형성을 이용하는 것이다. **`@classmethod` 다형성은 생성된 객체가 아니라 전체 클래스에 적용된다는 점만 빼면 _InputData.read()_ 에 사용한 인스턴스 메서드 다형성과 똑같다.**  

이 발상을 맵리듀스 관련 클래스에 적용해보자. 여기서는 공통 인터페이스를 사용해 새 _InputData_ 인스턴스를 생성하는 범용 클래스 메소드로 _InputData_ 클래스를 확장한다.


```python
class GenericInputData:
    def read(self):
        raise NotImplementedError

    @classmethod
    def generate_inputs(cls, config):
        raise NotImplementedError
```

_generate\_inputs_ 메소드는 _GenericInputData_ 를 구현하는 서브클래스가 해석할 설정 파라미터를 담은 딕셔너리를 받는다. 다음 코드에서는 입력 파일들을 얻어올 디렉토리를 config로 알아낸다.


```python
class PathInputData(GenericInputData):
    #...

    def read(self):
        return open(self.path).read()

    @classmethod
    def generate_inputs(cls, config):
        data_dir = config['data_dir']
        for name in os.listdir(data_dir):
            yield cls(os.path.join(data_dir, name))
```

비슷하게 _GenericWorker_ 클래스에 _create\_workers_ 헬퍼를 작성한다. 여기서는 _input\_class_ 파라미터(_GenericInputData_ 의 서브클래스여야 함)로 필요한 입력을 만들어낸다. _cls()_ 를 범용 생성자로 사용해서 _GenericWorker_ 를 구현한 서브클래스의 인스턴스를 생성한다.

```python
class GenericWorker:
    #..

    def map(sef):
        raise NotImplementedError

    def reduce(self, other):
        raise NotImplementedError

    @classmethod
    def create_workers(cls, input_class, config):
        workers = []
        for input_data in input_class.generate_inputs(config):
            workers.append(cls(input_data))

        return workers
```

**위의 `input_class.generate_inputs` 호출이 바로 이번 장에서 말하는 클래스 다형성이다. _input\_class_ 가 어떤 서브클래스더라도 문제없이 사용 가능해서 재사용성이 증가한다.**

또한 **_create\_workers_ 가 \_\_init\_\_ 메소드를 직접 사용하지 않고 _GenericWorker_ 를 생성하는 또 다른 방법으로 _cls_ 를 호출함을 알 수 있다.**

아까 작성한 줄수를 세는 카운터 클래스는 부모 클래스만 변경하면 된다.

```python
class LineCountWorker(GenericWorker):
    # ...
```

마지막으로 _mapreduce_ 함수를 완전히 범용적으로 재작성할 차례다.

```python
def mapreduce(worker_class, input_class, config):
    workers = worker_class.create_workers(input_class, config)
    return execute(workers)
```

결과는 같다. 변한 점은 새로운 함수는 동작을 위해 더 많은 파라미터를 요구한다는 점인데 그래도 이를 통해 얻는 이익이 비용을 훨씬 상회한다. 앞서 말한대로, 필요에 따라 기존과 다른 데이터 로드 클래스, 워커 생성 클래스를 써야 할 때 첫 번째 코드는 클래스 이름을 다 바꿔줘야 한다. 하지만 두 번째 _mapreduce_ 는 그렇지 않다. 


<br>

## 5. 핵심 정리

* 파이썬에서는 클래스마다 생성자를 단 한 개만 만들 수 있다.
* 클래스에 필요한 다른 생성자를 정의하려면 `@classmethod`를 사용하자.
* 구체 서브클래스들을 만들고 연결하는 범용적인 방법을 제공하려면 클래스메소드 다형성을 이용하자.
