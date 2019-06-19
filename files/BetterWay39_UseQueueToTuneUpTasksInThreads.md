## Better Way 39. 스레드 간의 작업을 조율하려면 Queue를 사용하자

#### 188쪽

* Created : 2019/06/19
* Modified: 2019/06/19

<br>

## 1. 생산자-소비자 큐로 스레드 파이프라인 구축하기

많은 작업을 동시에 실행하는 파이썬 프로그램에서는 종종 작업들을 조율해줘야 한다. 가장 유용한 작업 방식 중 하나는 `함수의 파이프라인`(pipeline)이다.  

여기서 파이프라인이라 함은 유닉스 쉘의 파이프라이닝과 유사하다. 쉘에서는 '\|'을 구분자로 써서 프로세스의 출력을 다른 프로세스의 입력으로 전환하고 이 작업을 연쇄적으로 진행할 수 있었다.


```shell
$ cat ok.py | sort | uniq | wc -w

;...
```

파이썬에서도 이와 같은 일을 잘할 수 있으며 파이썬으로 쉽게 병렬화할 수 있는 블로킹 I/O나 서브프로세스를 이용하는 작업에 특히 잘 맞는다.  

이번에 사용하는 예제는 다음과 같다. 디지털 마케라에서 끊임없이 이미지들을 다운로드해서 리사이즈하고, 온라인 포토 갤러리에 업로드하는 시스템을 구축한다고 하자. 이런 프로그램에서는 파이프라인을 세 단계로 나눌 수 있다.

1. 새 이미지를 카메라에서 추출한다.
1. 리사이즈 함수로 다운로드된 이미지를 처리한다.
1. 업로드 함수로 리사이즈된 이미지를 소비한다.

편의를 위해 이 세 가지 기능은 이미 구현되어 있다고 하자. 이때 **스레드를 사용해 작업을 동시에 처리하려면 파이프라인을 어떻게 조립해야 할까?**  

가장 먼저 필요한 건 파이프라인 단계에서 작업을 전달할 방법이다. [지난 장](https://github.com/shoark7/Effective-Python/blob/master/files/BetterWay38_UseLockForRaceConditionInThread.md)에서 여러 스레드가 공유 가능한 메모리를 통해 소통하는 `shared memory` 기법을 사용했었다. 이번에는 대표적인 대안인 `스레드 안전 생산자-소비자 큐`(thread-safe producer-consumer queue) 디자인 패턴으로 모델링해보자.  

이 방법은 입력을 큐에 집어넣는 생산자와 큐에서 아이템을 추출해 사용하는 소비자로 나눠 프로세스간(또는 스레드간) 통신을 가능케한다. **우리 예제에서는 저 세 가지 기능이 각각 생산자가 되고 소비자가 될 것이다.** 가령 추출한 이미지를 큐에 넣으면 리사이즈 함수가 이를 추출해 사용한다. 또 리사이즈된 이미지는 다른 큐에 입력되어 업로드 함수가 추출해 사용하게 될 것이다.

참고로 관련 내용은 [여기](http://web.mit.edu/6.005/www/fa15/classes/22-queues/)를 읽어보면 도움이 많이 된다.

첫 예제를 만들어보자.


```python
from collections import deque
from threading import Lock, Thread

class MyQueue:
    def __init__(self):
        self.items = deque()
        self.lock = Lock()

    def put(self, item):
        with self.lock:
            self.items.append(item)

    def get(self):
        with self.lock:
            return self.items.popleft()
```

각 기능이 사용할 큐를 정의했다. _deque_ 는 파이썬의 'Double Ended Queue'로서 입력과 출력 작업(task)을 할 때 사용할 것이다. 파이썬의 _list_ 는 큐로서는 성능이 안 좋기 때문에 이 자료구조를 사용한 것 같다. 다음으로 각 작업에 대한 단일성을 보장하는 Lock 변수를 선언한다.

_put_ 메소드는 큐가 생산자로 동작할 때 입력을 넣는 역할을 한다. Lock을 사용한다. _get_ 메소드는 반대로 큐가 소비자로 동잘할 때 큐의 값을 얻어오는 역할을 한다.


<br>

이제 이 큐를 이용해 작업을 꺼내와서 함수를 실행한 후 결과를 또 다른 큐에 넣는 파이썬 스레드로 파이프라인의 각 단계를 표현한다. 또한 작업 스레드가 새 입력을 몇 번이나 체크하고, 작업을 얼마나 완료하는지 추적한다.

```python
class Worker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.polled_count = 0 # 입력이 없을 때 상태를 확인한 횟수 계산
        self.work_done = 0
```

**가장 까다로운 부분은 이전 단계에서(리사이즈 함수 입장에서는 이미지 추출, 업로드 함수 입장에서는 리사이즈) 아직 작업을 완료하지 않아서 입력 큐가 비어 있는 경우를 작업 스레드에서 적절하게 처리하는 것이다.** 다음 코드에서 IndexError 예외를 잡는 부분이 이에 해당한다. 이 경우는 실제 공장의 조립 라인이 병목현상으로 정체된 상황에 비유할 수 있다.

```python
import time

class Worker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        # ...

    def run(self):
        while True:
            self.polled_count += 1
            try:
                item = self.in_queue.get()
            except IndexError:
                time.sleep(0.01) # 처리할 아이템이 없어서 대기
            else:
                result = self.func(item)
                self.out_queue.put(result)
                self.work_done += 1
```

이제 작업 조율용 큐와 그에 해당하는 작업 스레드를 생성해서 세 단계를 연결하면 된다.

```python
download_queue = MyQueue()
resize_queue = MyQueue()
upload_queue = MyQueue()
done_queue = MyQueue()

threads = [
    Worker(download, download_queue, resize_queue),
    Worker(resize, resize_queue, upload_queue),
    Worker(upload, upload_queue, done_queue)
]
```

첫 세 개의 큐는 각 기능을 위한 큐를 만든다. **각 기능은 파이프라인에서 생산자와 소비자의 역할을 겸임하기 때문에 이를 위해 각각 큐를 할당해 사용한다.** *done\_queue* 는 완료된 작업을 저장하기 위해 할당했다.

다음으로 _threads_ 리스트에 각 기능에 대한 스레드 워커를 입력한다. 각 워커의 인자는 수행할 함수(기능), 입력 큐, 출력 큐가 된다.

<br>

스레드를 시작하고 파이프라인의 첫 번째 단계에 많은 작업을 추가한다. 다음 코드에서는 _download_ 함수에 실제 데이터 대신 일반 _object_ 인스턴스를 사용했다.

```python
SIZE = 1000

for thread in threads:
    thread.start()

for _ in range(SIZE):
    download_queue.put(object())


while len(done_queue.items) < SIZE:
    # 스레드 실행 동안
    # 메인 스레드의 다른 작업 실행
    pass
```

이 코드는 _download_, _resize_, _upload_ 함수가 아무 값이나 반환하게 정의하고 실행해보면 제대로 동작은 한다. 하지만 지금까지의 코드는 사실 여러 문제가 있다. 다음 장에서 확인할 것이다.


<br>

## 2. 첫 번째 방법의 문제점

이전 장에서 생산자, 소비자 큐 디자인 패턴으로 각 기능들의 처리를 원만히 해결한 것으로 보인다. 하지만 이 방법에는 여러 가지 문제점이 있다.


먼저 _run_ 메소드를 다시 한 번 살펴보자.

```python
def run(self):
    while True:
        self.polled_count += 1
        try:
    	    item = self.in_queue.get()
        except IndexError:
    	    time.sleep(0.01)
        else:
    	    result = self.func(item)
    	    self.out_queue.put(result)
    	    self.work_done += 1
```

가장 바람직한 상황은 각 기능의 동작속도가 일정해서 큐에 입력되고 소비되는 프로세스가 막힘 없이 흘러가는 상황일 것이다. 하지만 병목현상이 발생해서 한 기능이 입력을 수없이 기다려야 한다면 이는 문제가 된다. 즉, 이 코드에서는 파이프라인에 정체가 생길 수 있다.  

한 번 확인해보자.

```python
processed = len(done_queue.items)
polled = sum(t.polled_count for t in threads)
print(processed, polled)


1000 3011
```

_poll_ 은 스레드의 상태를 확인하고 기다리는 역할을 한다. 출력물에서 우리가 진행한 작업(task)은 1000회인데, 이를 기다리는 일은 3000여번이나 한 것을 알 수 있다. 결국 **작업 스레드는 유용한 작업을 전혀 하지 않으면서 CPU 시간을 낭비한다.**(끊임없이 IndexError를 일으키고 잡는 일만 한다.)

<br>

이외에도 몇 개의 문제점이 더 있다. 

1. 입력을 모두 완료했는지 판단하려면 *done\_queue* 에 결과가 모두 쌓일 때까지 기다려야 한다.
1. Worker의 run 메소드는 루프에서 끊임없이 실행된다.
1. **파이프라인의 정체로 시스템이 다운되는 최악의 상황에 놓일 수 있다.**

특히 마지막 문제점은 심각하다. 예를 들어 첫 번째 단계는 빠르게 진행하지만 두 번째 단계는 느리게 진행하면, 두 단계를 연결하는 큐의 크기가 계속 증가한다. 즉, **메모리 부족으로 프로그램이 죽을 수 있다.**

여기서 얻을 교훈은 파이프라인이 나쁘다는 게 아니라 좋은 생산자-소비자 큐를 직접 만들기가 그만큼 어렵다는 사실이다.

<br>

## 3. 해결책: Queue 내장 클래스 사용하기

이에 대한 적절한 해결책은 내장 모듈 queue의 Queue 클래스를 사용하는 것이다. **queue 모듈은 동기화된 큐 클래스를 제공하는 모듈로서 다사용자, 다소비자에 적절한 큐를 구현한 고수준의 API이다.** Queue 클래스는 스레드 사용 환경에 특화되어 있어 이미 내부적으로 필요한 Lock 환경을 갖춰놓고 있다. 관련 문서는 [여기](https://docs.python.org/3/library/queue.html)서 확인하면 된다.

Queue는 스레드 안전 생산자-소비자 큐와 관련된 여러 메소드를 구현하고 있는데 이들의 구체적인 내용은 문서로 확인하길 바란다.

**Queue 클래스는 새 데이터가 생길 때까지 _get_ 메소드가 블록되게 하여 작업 스레드가 계속해서 데이터가 있는지 체크하는 상황(busy waiting)을 없애준다.** 예를 들어 다음은 큐에서 입력 데이터를 기다리는 스레드를 시작한다.

```python
from queue import Queue

queue = Queue()

def consumer():
    print('Consumer waiting')
    queue.get()
    print('Consumer done')

thread = Thread(target=consumer)
thread.start()
```

**스레드가 처음으로 실행할 때도 Queue 인스턴스에 아이템이 들어가서 get 메소드에서 반환할 아이템이 생기기 전에는 마치지 못한다.**

```python
print('Producer putting')
queue.put(object())
thread.join()
print('Producer done')
```

위의 두 블록의 실행결과 print 문의 순서는 다음과 같다. 순서를 눈여겨 보자.

```python
Consumer waiting
Producer putting
Consumer done
Producer done
```

스레드가 시작하면서 소비자는 get을 하면서 입력을 기다리고 있다. 그 다음에 생산자가 아이템을 넣으면 get에서 아이템을 반환해 작업을 처리하고 소비자의 일을 마무리한다. 마지막으로 스레드의 join을 마치며 생산자도 마무리한다.

<Br>

파이프라인 정체 문제를 해결하려면 두 단계 사이에서 대기할 작업의 최대개수를 Queue에 설정해야 한다. **큐가 이미 이 버퍼 크기만큼 가득 차 있으면 put 호출이 블록된다.** 예를 들어 다음 코드는 큐를 소비하기 전에 잠시 대기하는 스레드를 정의한다.

```python
import time

queue = Queue(1) # 최대 크기를 1로 지정

def consumer():
    time.sleep(0.1)
    queue.get()
    print('Consumer got 1')
    queue.get()
    print('Consumer got 2')


thread = Thread(target=consumer)
thread.start()
```

대기 결과로 consumer 스레드에서 get을 호출하기 전에 생산 스레드에서 put으로 객체 두 개를 큐에 집어넣는 동작이 일어나야 한다. 하지만 Queue의 크기가 1이다. 다시 말해, **두 번째 put 호출이 블록된 상태에서 빠져나와서 두 번째 아이템을 큐에 넣을 수 있으려면, 큐에 아이템을 추가하는 생산자는 소비 스레드에서 적어도 한 번은 get을 호출하기를 기다려야 한다.**

```python
queue.put(object())
print('Producer put 1')
queue.put(object())
print('Producer put 2')
thread.join()
print('Producer done')
```

위 두 블록의 실행결과는 다음과 같다.

```python
Producer put 1
Consumer got 1
Producer put 2
Consumer got 2
Producer done
```

생산자의 두 번째 입력이 소비자의 아이템 획득이 한 번 진행되어야 가능해짐을 알 수 있다. 큐의 최대 크기가 1이기 때문에 put이 자동으로 블록됐다.

<br>

## 4. 첫 번째 코드 개선

이전 장에서 Queue에 대한 기본적인 내용을 이해했다. 이제 이를 실제 활용해서 첫 번째 코드를 개선해보자.  

먼저 아까는 deque를 썼다면 이번에는 Queue를 상속하는 서브클래스를 만들자. 이때 입력의 마지막을 표편할 수 있도록 close 메소드를 만든다.

```python
class ClosableQueue(Queue):
    SENTINEL = object()

    def close(self):
        self.put(self.SENTINEL)

    def __iter__(self):
        while True:
            item = self.get()
            try:
                if item is self.SENTINEL:
                    return
                yield item
            finally:
                self.task_done()
```

이제는 이 큐에 맞는 스레드 워커를 만든다. 스레드는 for 루프가 끝나면 종료한다.


```python
class StoppableWorker(Thread):
    def __init__(self, func, in_queue, out_queue):
        # 위와 같음
        pass

    def run(self):
        for item in self.in_queue:
            result = self.func(item)
            self.out_queue.put(result)
```

다음으로 새 작업 클래스를 사용하여 작업 스레드를 다시 생성한다.

```python
class StoppableWorker(Thread):
    def __init__(self, func, in_queue, out_queue):
        # 위와 같음
        pass

    def run(self):
        for item in self.in_queue:
            result = self.func(item)
            self.out_queue.put(result)
```



```python
download_queue = ClosableQueue()

threads = [
    StoppableWorker(download. download_queue, resize_queue)
]

for thread in threads:
    thread.start()

for _ in range(1000):
    download_queue.put(object())

download_queue.close()
```

<br>

## 5. 핵심 정리

* 파이프라인은 여러 파이썬 스레드를 사용하여 동시에 실행하는 작업의 순서를 구성하기에 아주 좋은 방법이다.
* 병행 파이프라인을 구축할 때는 많은 분제(바쁜 대기, 작업자 중단, 메모리 부족)가 일어날 수 있다는 점을 주의하자.
* Queue 클래스는 연산 블로킹, 버퍼 크기, 조인 등 견고한 파이프라인을 만드는 데 필요한 기능을 모두 갖추고 있다.
