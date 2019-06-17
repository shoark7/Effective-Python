## Better Way 38. 스레드에서 데이터 경쟁을 막으려면 Lock을 사용하자

#### 183쪽

* Created : 2019/06/17
* Modified: 2019/06/17

<br>

## 1. GIL은 데이터의 경쟁을 보호하지 못한다.

파이썬의 GIL을 배우고 나면, 나같은 신참 프로그래머가 **파이썬에서 상호 배제 잠금(MUTEX)을 사용하지 않아도 될 것이라 생각할지도 모른다.** v아씨너 스레드가 여러 CPU 코어에서 병렬로 실행하는 것을 GIL이 이미 막았다면 프로그램의 자료구조에도 잠금이 설정되어 있을 것이다. 충분히 생각해봄직 하다.

하지만 실제로는 그렇지 않다. GIL로 인해 파이썬 스레드가 한 번에 하나만 실행되지만, **파이썬 인터프리터에서 자료구조를 다루는 스레드 연산은 두 바이트코드 명령어 사이에서 인터럽트될 수 있다. 특히 여러 스레드에서 동시에 같은 객체에 접근한다면 이런 가정은 위험하다.** 자료구조의 불변성이 인터럽트 때문에 언제든지 깨질 수도 있다는 의미이며 프로그램은 오류가 있는 상태로 남는다.

예를 들어, 전체 센서 네트워크에서 밝기 단계를 샘플링하는 경우처럼 병렬로 여러 대상을 카운트하는 프로그램을 작성한다고 해보자. 시간에 따른 밝기 샘플의 전체 개수를 알고 싶다면 새 클래스로 개수를 모으면 된다.


```python
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self, offset):
        self.count += offset
```

센서에서 읽는 작업에서는 블로킹 I/O가 필요하므로 각 센서별로 고유한 작업 스레드를 만들어 해결하면 될 것 같다.([37장](https://github.com/shoark7/Effective-Python/blob/master/files/BetterWay37_UseThreadForIO.md) 참조) 각 센서 측정값을 읽고 나면 작업 스레드는 읽으려는 최대 개수에 이를 때까지 카운터를 증가시킨다.

```python
def worker(sensor_index, how_many, counter):
    for _ in range(how_many):
        # ... 센서에서 읽는 I/O
	# ... sensor_index를 사용해 네트워크 내 특정 센서를 지목할 듯

        counter.increment(1)
```

이제 스레드를 만들어서 센서별로 작업 스레드를 시작하고 읽기를 모두 마칠 때까지 기다리는 함수다.

```python
from threading import Thread

def run_threads(func, how_many, counter):
    SIZE = 5
    threads = []

    for i in range(SIZE):
        args = (i, how_many, counter)
        thread = Thread(target=func, args=args)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
```

스레드 5개를 병렬로 실행하는 일은 간단해 보이므로 결과가 명확하 것으로 보인다.


```python
how_many = 10 ** 5
counter = Counter()
run_threads(worker, how_many, counter)
print(f'Counter should be 500,000 and the real result is {counter.count:,}')


Counter should be 500,000 and the real result is 328,223
```

센서를 읽는 작업을 50만번이나 했기 때문에 실제 카운터도 50만이 찍히리라 무난히 생각할 수 있다. 하지만 예상과는 다르게 약 33만으로 더 적게 나왔다. 왜 그럴까?

파이썬 인터프리터는 모든 스레드가 거의 동등한 처리 시간 동안 실행하게 하려고 모든 실행 중인 스레드 사이에서 공평성을 유지한다. **파이썬은 공평성을 유지하려고 실행 중인 스레드를 잠시 중지하고 차례로 다른 스레드를 재개한다. 문제는 파이썬이 스레드를 정확히 언제 중지할지 모른다는 점이다.** 스레드는 심지어 원자적(atomic)인 연산으로 보이는 작업 중간에서 멈출 수도 있다.


```python
self.count += offset
```

앞선 카운터에서 _offset_ 만큼 카운트를 증가시키는 코드다. 언뜻 보기에 이 작업은 단일한, 원자적인 작업 같지만 '+=' 연산자는 실제로는 다음과 같은 코드가 실행된다.

```python
value = getattr(counter, 'count')
result = value + offset
setattr(counter, 'count', result)
```

카운터를 증가시키는 파이썬 스레드는 이 연산들 사이에서 중지될 수 있다. 만약 연산이 끼어든 상황 때문에 value 이전 값이 카운터에 할당되면 문제가 된다. 다음은 두 스레드 A, B 사이의 안 좋은 상호작용을 보여주는 예다.

```python
value_a = getattr(counter, 'count')
value_b = getattr(counter, 'count')
result_b = value_b + 1
setattr(counter, 'count', reult_b)
result_a = value_a + 1
setattr(counter, 'count', result_a)
```

스레드 A는 스레드 B에서 카운터 증가를 실행하는 모든 작업을 없앤다. 이런 일이 앞선 예제에서 발생해서 실제 값보다 적게 나오게 된 것이다.

<br>

## 2. 해결책: Lock 사용하기

**파이썬은 이와 같은 데이터 경쟁(race)과 다른 방식의 자료구조 오염을 막으려고 내장 모듈 threading에 강력한 도구들을 갖춰놓고 있다. 가장 간단하고 유용한 도구는 상호 배제 잠금 기능을 제공하는 Lock 클래스를 사용하는 것이다.**

잠금을 이용하면 여러 스레드가 동시에 접근하더라도 Counter 클래스의 현재 값을 보호할 수 있다. 한 번에 한 스레드만 잠금을 얻을 수 있다. 여기에 `with` statement를 사용해서 만들어보자.


```python
from threading import Lock

class LockingCounter:
    def __init__(self):
        self.lock = Lock()
        self.count = 0

    def increment(self, offset):
        with self.lock:
            self.count += offset
```

이제 전처럼 작업 스레드를 실행하지만 이번에는 _LockingCounter_ 를 사용한다.

```python
how_many = 10 ** 5
counter = LockingCounter()
run_threads(worker, how_many, counter)
print(f'Counter should be 500,000 and the real result is {counter.count:,}')


Counter should be 500,000 and the real result is 500,000
```

결과가 예상한 것과 정확히 일치한다. Lock를 보유한 스레드에 _offset_ 을 추가하는 작업이 점유되기 때문에 중간에 작업이 강탈당하지 않는다. 대신 시간이 좀더 걸린다.


<br>

## 3. 핵심 정리

* 파이썬에 GIL이 있다고 해도 프로그램 안에서 실행되는 스레드 간의 데이터 경쟁으로부터 보호할 책임은 프로그래머에게 있다.
* 여러 스레드가 잠금 없이 같은 객체를 수정하면 프로그램의 자료구조가 오염된다.
* 내장 모듈 threading의 Lock 클래스는 파이썬의 표준 상호 배제 잠금 구현이다.
