## Better Way 43. 재사용 가능한 try/finally 동작을 만들려면 contextlib과 with 문을 고려하자

#### 218쪽

* Created : 2017/08/17
* Modified: 2019/06/22

<br>

## 1. contextmanager 소개

**파이썬의 'with' 문은 코드를 특별한 컨텍스트(context)에서 실행함을 나타내는 데 사용한다.** 예를 들어 [38장](https://github.com/shoark7/Effective-Python/blob/master/files/BetterWay38_UseLockForRaceConditionInThread.md)에서 살펴본 것처럼 'with'문에 MUTEX를 사용하여 잠금이 설정되어 있는 동안만 들여 쓴 코드를 쓰는 예제를 확인했다.

```python
import threading

lock = threading.Lock()
with lock:
    print("Lock is held by me!")
```

**Lock 클래스가 with문을 제대로 지원하는 덕분에 위의 코드는 다음의 try / finally 구문에 상응한다.**

```python
lock.acquire()
try:
    print("Lock is help by me!")
finally:
    lock.release()
```

위의 두 코드가 같은 일을 한다면 어떤 방법이 더 좋은 practice일까? 일반적으로 같은 성능이면 코드를 줄일 수 있으면 좋다. 그런 의미에서 try / finally 구문에서 반복되는 코드를 작성할 필요가 없는 with 문 버전이 더 낫다.

**내장 모듈 contextlib를 사용하면 객체와 함수를 with 문에 사용할 수 있게 만들기가 쉽다.** 이 모듈은 간단한 함수를 with 문에 사용할 수 있게 해주는 `contextmanager` 데코레이터를 포함한다. 이 데코레이터를 이용하는 방법이 \_\_enter\_\_, \_\_exit\_\_라는 특별한 메소드를 담은 새 클래스를 정의하는 표준 방법보다 훨씬 쉽다.


<br>

이번에 사용할 예제는 내장 `logging` 모듈로 만들어보자. 로그는 상황에 따라 다양한 수준의 로그를 남기는데 가끔씩은 코드의 특정 영역에 더 많은 디버깅 로그를 넣고 싶다고 해보자. 여기서는 로깅 심각성 수준(severity level) 두 개로 로그를 남기는 함수를 정의한다.

이 포스트에서는 `logging` 모듈의 자세한 내용은 생략하도록 하겠다. 필요한 분들은 [공식 문서](https://docs.python.org/3/library/logging.html)를 확인하기 바란다.


```python
def my_function():
    logging.debug("Some bug happended")
    logging.error("Something very bad;")
    logging.debug("Another small bug got caught!")
```

따로 값을 주지 않았을 때, 로깅 프로그램의 기본 로그 수준은 'WARNING'이다. 따라서 함수를 실행하면 에러 로그만 출력되고 디버그 로그는 출력되지 않는다.

```python
import logging

def my_function():
    logging.debug("Some bug happended")
    logging.error("Something very bad;")
    logging.debug("Another small bug got caught!")

my_function()


ERROR:root:Something very bad; # debug수준 에러는 무시됨.
```

<Br>

컨텍스트 매니저를 정의하여 이 함수의 로그 수준을 임시로 높일 수 있다. 이 헬퍼 함수는 with 블록에서 코드를 실행하기 전에 로그 심각성 수준을 높이고 실행 후에는 다시 낮춘다.


```python
from contextlib import contextmanager

@contextmanager
def debug_logging(level):
    logger = logging.getLogger()
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)

    try:
        yield
    finally:
        logger.setLevel(old_level)
```

여기서 `yield` 식을 주목하자. 어떤 반환값도 없는 것을 볼 수 있는데 **이 'contextmanager' 데코레이터에서는 yield 지점이 'with' 블록의 내용이 실행되는 지점이다.** with 블록에서 일어나는 모든 예외를 yield 표현식이 다시 일으키므로 헬퍼 함수로 처리할 수 있다.  

이제 같은 로깅 함수를 *debug\_logging* 컨텍스트에서 호출한다. 이번에는 with 블록 안에 있는 디버그 메시지가 모두 화면에 출력된다. 같은 함수를 with 블록 외부에서 실행하면 디버깅 메시지가 출력되지 않는다.

```python
with debug_logging(logging.DEBUG):
    print("Inside:")
    my_function()

print("\nAfter:")
my_function()


Inside:
DEBUG:root:Some bug happended
ERROR:root:Something very bad;
DEBUG:root:Another small bug got caught!

After:
ERROR:root:Something very bad;
```


<br>

## 2. `as`로 타깃 지정하기

파이썬에서 파일을 열고 닫을 때 'as'로 파일 객체를 지정했던 것을 기억할 것이다.

```python
with open("somefile.txt") as fd: # fd라는 파일 객체 선언
    pass
```

이것을 또한 contextmanager를 통해 지정할 수 있다. 이 기능을 이용하면 with 블록 안에 있는 코드에서 직접 컨텍스트와 상호작용할 수 있다.

함수에서 'as' 타깃에 값을 제공할 수 있게 하려면 컨텍스트 매니저에서 yield를 사용하여 값을 넘겨주기만 하면 된다.

예를 들어, 다음은 Logger 인스턴스를 가져와서 심각성 수준을 설정한 후 yield 인스턴스를 as에 전달하도록 정의한 예다.

```python
@contextmanager
def log_level(level, name):
    logger = logging.getLogger(name)
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)

    try:
        yield logger
    finally:
        logger.setLevel(old_level)
```

with 블록에서 로깅 심각성 수준을 충분히 낮게 설정했으니 as 값으로 debug 같은 로깅 메소드를 호출하면 출력이 나올 것이다. logging 모듈의 기본 로깅 심각성 수준은 WARNING이므로 logging 모듈을 직접 사용하면 아무것도 출력되지 않는다.

```python
@contextmanager
def log_level(level, name):
    logger = logging.getLogger(name)
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)

    try:
        yield logger
    finally:
        logger.setLevel(old_level)


with log_level(logging.DEBUG, 'my-log') as logger:
    logger.debug("This is my debug message!")
    logging.debug("This will not be printed")


DEBUG:my-log:This is my debug message! # logger의 로그만 출력됨.
```

with 문이 종료한 후에 'my-log'라는 Logger의 디버그 로깅 메소드를 호출하면, 기본 로깅 심각성 수준으로 되돌아간 뒤라서 아무것도 출력되지 않는다. 물론 오류 로그 메시지는 항상 출력된다.

```python
logger = logging.getLogger('my-log')
logger.debug("Debug message will not print")
logger.error("Something really bad happened")


ERROR:my-log:Something really bad happened
```

<Br>

## 3. 핵심 정리

* with 문을 이용하면 try / finally 블록의 로직을 재사용할 수 있고, 코드를 깔끔하게 만들 수 있다.
* 내장 모듈 contextlib의 contextmanager 데코레이터를 이용하면 직접 작성한 함수를 with 문에서 쉽게 사용할 수 있다.
* 컨텍스트 매니저에서 넘겨준 값은 with 문의 as 부분에 할당된다. 컨텍스트 매니저에서 값을 반환하는 방법은 코드에서 특별한 컨텍스트에 직접 접근하려는 경우에 유용하다.
