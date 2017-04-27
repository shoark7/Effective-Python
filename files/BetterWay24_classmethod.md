## Better Way 24. 객체를 범용으로 생성하려면 @classmethod 다형성을 이용하자

## 102쪽

### 2017/04/27 작성.


파이썬에서는 클래스의 다형성이 잘 지원된다. 이것은 어떤 의미이고 어떤 장점이 있을까?  

**다형성은 계층 구조에 속한 여러 클래스가 자체의 메서드를 독립적인 버전으로 구현하는 방식**이다.  
다형성을 이용하면 여러 클래스가 같은 인터페이스나 추상 기반 클래스를 충족하면서도  
다른 기능을 제공할 수 있다.(collections.abc의 여러 클래스들 참고)  

\* 책에서의 예제는 맵리듀스(이하 _mapreduce_)를 구현하면서 다형성을 설명하는데,  
사실 예제가 다소 어렵다. _mapreduce_에 대한 기본적인 이해가 필요하고,  
코드 자체도 유심히 봐야하는 면이 있다. 하지만 분명히 많이 배울 수 있다. 자신한다.  
[what is MapReduce](https://www-01.ibm.com/software/data/infosphere/hadoop/mapreduce/) <- 이곳을 참고하라.

시작하자.  
<br><Br>


### Part 1. _mapreduce_ 기본 구현
#### 1.1 데이터 입력 받기
_mapreduce_ 구현을 작성할 때 먼저 입력 데이터를 표현할 공통 클래스가 필요하다.  
다음은 서브클래스에서 정의해야 하는 read 메서드가 있는 입력 데이터 클래스다.  

```python
import os
from threading import Thread


class InputData:
    def read(self):
        raise NotImplementedError


class PathInputData(InputData):
    def __init__(self, path):
        super().__init__()
        self.path = path

    def read(self):
        return open(self.path).read()
```  

`InputData`는 일종의 interface이고, `PathInputData`는 mapreduce를 위한 구현체이다.  
`PathInputData`는 경로를 입력 받으면 read 메서드를 통해 파일을 읽어들인다.  

`PathInputData`와 같은 `InputData`의 서브클래스는 얼마든지 만들 수 있다.  
예를 들면 네트워크에서 파일을 읽어들이거나 zip 파일을 압축, 읽는 클래스도 존재할 수 있다는 뜻이다.  
일단은 단순히 경로에서 파일을 읽는 예제를 사용한다.  

<br>
#### 1.2 map, reduce 구현하기
다음에는 입력을 받아 map, reduce를 실행하는 클래스를 생성한다.  
이번 예제에서 map task는 입력 데이터에서 줄의 개수('\\n')를 세는 일을 한다.


```python
class Worker:
    def __init__(self, input_data):
        self.input_data = input_data
        self.result = None

    def map(self):
        raise NotImplementedError

    def reduce(self, other):
        raise NotImplementedError


class LineCountWorker(Worker):
    def map(self):
        data = self.input_data.read()
        self.result = data.count('\n')

    def reduce(self, other):
        self.result += other.result
```
`LineCountWorker` 클래스는 `Worker` 클래스를 상속받아서 `map`, `reduce` 메서드를 구현한다.  
`map` 메서드는 데이터를 읽어 줄의 개수를 세고,  
`reduce`는 다른 map task의 줄의 개수를 합치는 일을 한다.  

이제 직면한 문제는 이 클래스들을 사용하여 실제로 map, reduce를 실행하는 코드이다.  
간단한 방법은 **헬퍼 함수를 만들어 만든 클래스들의 객체를 활용하는 방법이다.**  

먼저 경로를 입력 받아 경로 안의 모든 파일로 PathInputData 객체를 생성하는 함수를 만든다.  

```python
def generate_inputs(data_dir):
    for name in os.listdir(data_dir):
        yield PathInputData(os.path.join(data_dir, name))
```
`os.path.join`과 `yield`를 활용했다는 점을 눈여겨보면 좋겠다.  


다음은 `generate_inputs` 함수가 반환한 `InputData` 인스턴스를 사용하는  
`LineCountWorker` 인스턴스를 생성하는 함수이다.  

```python
def create_workers(input_list):
    workers = []
    for input_data in input_list:
        workers.append(LineCountWorker(input_data))
    return workers
```


다음은 반환된 workers를 활용해 mapreduce를 실행하는 함수다.
```python
def execute(workers):
    threads = [Thread(target=w.map) for w in workers]
    for thread in threads: thread.start()
    for thread in threads: thread.join()

    first, rest = workers[0], workers[1:]
    for worker in rest:
        first.reduce(worker)
    return first.result
```

쓰레드를 활용했다는 점을 활용하면 좋겠다. 파이썬에서 IO는 쓰레드를 활용하면 좋다.  
오래 참았다. 마지막으로 이 세 함수를 엮는 template 함수다.

```python
def mapreduce(data_dir):
    inputs = generate_inputs(data_dir)
    workers = create_workers(inputs)
    return execute(workers)

    # 1. 경로를 입력 받아 각 파일을 대표하는 인스턴스(input)를 만든다.
    # 2. input을 통해 map, reduce가 가능한 workers를 만든다.
    # 3. workers의 map, reduce를 통해 최종 결과값을 구한다.
```

이 함수들을 활용해 클래스들의 기능을 사용해서 한 경로의 모든 파일의 줄 수를 구하는  
mapreduce를 구현했다.


```python
# Test code
from tempfile import TemporaryDirectory

def write_test_files(tmpdir):
    pass # Make or copy files to here for test.

with TemporaryDirectory() as tmpdir:
    write_test_files(tmpdir)
    result = mapreduce(tmpdir)

print("There are", result, "lines.")

>>> There are 4301 lines.
```


Test code이다. `tempfile`이라는 디렉토리를 공부하면 좋겠다.  

좋다. 잘 작동한다. 그런데 이 코드는 그다지 좋은 코드는 아니다.  
<br><br>

### Part 2. @classmethod를 통한 mapreduce 구현

아까 Worker와 Input 클래스의 여러 형태, 서브 클래스가 존재할 수 있다고 이야기 했다.  
분명 다른 용도로 서로 다른 서브클래스를 구현할 경우가 생길 수 있다.  
그런데 우리가 클래스들을 활용하는 함수들(generate\_inputs, execute, mapreduce 등)은  
우리가 구현한 서브 클래스가 직접적으로 사용되고 있다.  

다시 말해, **서브 클래스를 만들 때마다 위 함수들을 새롭게 정의하거나 코드를 일일이 수정해야 한다.**  
문제는 결국 객체를 생성하는 범용적인 방법의 필요성으로 귀결된다.  다른 언어에서는 이 문제를  
생성자 다형성으로 해결한다고 한다.  
하지만 파이썬에서는 클래스의 생성자는 \_\_init\_\_ 하나만이 유효하다.  

이 문제를 해결하는 가장 좋은 방법은 **@classmethod 다형성을 이용하는 것**이다.  
`@classmethod` 데코레이터는 클래스의 메서드를 인스턴스 메서드에서 클래스 메서드로 변환한다.  
@classmethod 데코레이터를 클래스의 메소드 바로 위에 사용하면  
그 메소드는 클래스 메소드가 되어 클래스 자체에서 직접 메소드를 사용할 수 있다.  

```python
class a:
    @classmethod
    def say(cls):
        print("I'm hungry!!")

a.say()

>>> I'm hungry!!
```

일반 메서드에서는 위 예제처럼 클래스 자체에서 메서드를 쓰면 오류가 발생한다.  
@classmethod 데코레이터를 사용했기에 클래스 자체에서 메서드를 사용할 수 있는 것이다.  
클래스 메서드의 첫 인자는 관습적으로 self 대신에 **cls**를 사용한다.  


@classmethod 다형성은 생성된 객체가 아니라 전체 클래스에 적용된다는 점만 빼면  
`InputData.read`에서 사용한 인스턴스 메서드 다형성과 똑같다.  


실제로 classmethod를 통해 위 예제를 다시 구현해보자.  
<br>

#### 2.1. 데이터 입력 받기
```python
class GenericInputData:
    def read(self):
        raise NotImplementedError

    @classmethod
    def generate_inputs(cls, config):
        raise NotImplementedError


class PathInputData2(GenericInputData):
    def __init__(self, path):
        super().__init__()
        self.path = path
        
    def read(self):
        return open(self.path).read()

    @classmethod
    def generate_inputs(cls, config):
        data_dir = config['data_dir']
        for name in os.listdir(data_dir):
            yield cls(os.path.join(data_dir, name))
```

앞서 정의했던 generate\_inputs 메서드가 GenericInputData 클래스의 클래스 메서드로 정의되었다.  
generate\_inputs의 모든 서브 클래스는 이 메서드를 구현해야 한다.  
`config`는 서브클래스가 해석할 설정 파라미터들을 담은 딕셔너리를 받는다.

주목할 것은 클래스 메서드에서 인자 `cls`를 통해 직접 객체를 생성할 수 있다는 점이다.  
아까와 달리 추가 함수를 통해 객체를 만들지 않아도 되고, 모든 GenericInputData의 서브 클래스들이  
가지고 있는 generate\_inputs 메서드를 범용적으로 사용할 수 있다.

다음은 input으로 map, reduce를 시행할 수 있는 GenericWorker도 위와 유사하게 작성해보자.  
<br>


#### 2.2. map, reduce 구현하기
```python
class GenericWorker:
    def __init__(self, input_data):
        self.input_data = input_data
        self.result = None

    def map(self):
        raise NotImplementedError

    def reduce(self, other):
        raise NotImplementedError

    @classmethod
    def create_workers(cls, input_class, config):
        workers = []
        for input_data in input_class.generate_inputs(config):
            workers.append(cls(input_data))
        return workers


class LineCountWorker2(GenericWorker):
    def map(self):
        data = self.input_data.read()
        self.result = data.count('\n')

    def reduce(self, other):
        self.result += other.result
```
GenericWorker의 classmethod인 `create_workers`도 자신의 인스턴스를 직접 생성하고 있다.  
코드 안의 `input_class.generate_inputs`가 바로 클래스 다형성이다.  

우리가 어떤 InputData의 서브클래스를 구현하든, 그것들이 구현하고 있는 generate\_inputs를  
범용적으로 사용할 수 있다. 코드 추가, 수정이 필요하지 않은 것이다.


마지막으로 mapreduce 함수를 완전히 범용적으로 재작성하자.

```python
def mapreduce2(worker_class, input_class, config):
    workers = worker_class.create_workers(input_class, config)
    return execute(workers)
```

이전에 구현할 것과 결과가 동일하지만 범용적으로 동작하기 위해 더 많은 파라미터를 요구한다.


```python
# Test code
with TemporaryDirectory() as tmpdir:
    write_test_files(tmpdir)
    config = {'data_dir': tmpdir}
    result = mapreduce2(LineCountWorker2, PathInputData2, config)
```

이제 GenericInputData와 GenericWorker의 다른 서브클래스를 원하는 대로 만들어도
글루 코드(glue code)를 작성할 필요가 없다.  


개인적으로 파이썬에서 그냥 메서드 쓰면 되지 classmethod가 무슨 특별한 의미가 있냐고 생각했는데  
이번 예제를 통해 그런 편견을 고쳤다. 좀 더 능동적으로, 개방적으로 질문을 던지고 알아가야겠다.
<br><BR>


### 핵심정리
* 파이썬에서는 클래스별로 생성자를 한 개(\_\_init\_\_ 메서드)만 만들 수 있다.
* 클래스에 필요한 다른 생성자를 정의하려면 @classmethod 데코레이터를 사용하자.
* 구체적인 서브 클래스들을 만들고 연결하는 범용적인 방법을 제공하려면 클래스 메서드 다형성을 이용하자.
