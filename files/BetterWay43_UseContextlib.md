# BetterWay 43. 재사용 가능한 try/finally 동작을 만들려면 contextlib과 with 문을 고려하자.


#### 218쪽
#### 2017/08/17 작성 

고백컨대 난 [contextlib](https://docs.python.org/3/library/contextlib.html) 내장모듈을 처음 보았다. 파이썬을 공부 좀 했다고 생각했는데  
아직 멀었다고 생각한다. 제목에 with 문을 언급하고 있는데 뒤에 확인하겠지만 contextlib과 관련이 있다.  

<br>

## Part 1. contextlib?

먼저 with 문에 대해 먼저 생각해보자.  

파이썬에서 with 문은 보통 튜토리얼에서 처음 접했을 것이다.

```python
with open('text.txt', 'r+') as fd:
    sentences = fd.read()
    for line in sentences:
        print(line)

    ...
```

위에서 with 문 안에서 파일을 열고 그 파일 객체를 fd로 할당한다.  
그리고 코드 안에서 fd를 사용했다. 아마 with 사용을 권장받았을텐데 그 이유는  
with 블록이 끝나면서 자동으로 fd 파일 객체가 닫히기 때문이다.  
그래서 프로그래머가 파일을 닫지 않는 실수를 할 여지가 없다.  
프로그래머가 의도하지 않은 동작을 자동으로 해결해줬는데 이를 위해서는
\_\_enter\_\_, \_\_exit\_\_ 메소드를 클래스에 구현해야 한다.
그 클래스의 인스턴스는 with 문 안에서 구현한 추가 동작이 실행되게 된다.
관심이 있으면 이 메소드들에 대해 찾아보도록 한다.  

익숙한 파일 객체뿐만 아닌 with를 사용한 다른 객체의 예도 살펴보자.
[threading](https://docs.python.org/3/library/threading.html) 모듈의 Lock 클래스를 사용한 예제이다.

```python
from threading import Lock


lock = Lock()
with lock:
    print('Lock is held')
```

<br>
Lock 클래스에는 with 문에 대한 추가 동작이 설정되어 있어 **Lock를 획득하고 해제하는 동작이 자동 실행된다.**  
따라서 위 코드는 다음 코드와 본질적으로 동일하다.

```python
lock.acquire()

try:
    print("Lock is held")
finally:
    lock.release()
```

<br>
두 코드를 비교하면 try/finally 구문에서 반복되는 코드를 작성할 필요가 없는 with 문 버전이 더 낫다.  
with 문 안에 있는 블록은 하나의 context라고 할 수 있으며 contextlib 모듈은 이런 컨텍스트에 대해 다룬다.  
내장모듈 contextlib을 사용하면 객체와 함수를 with 문에 사용할 수 있게 만들기 쉽다.  
이 모듈은 간단한 함수를 with 문에 사용할 수 있게 하는 **contextmanager** 데코레이터를 포함한다.  
이 데코레이터를 사용하는 것이 \_\_enter\_\_와 \_\_exit\_\_이라는 특수 메서드를 담은  
새 클래스를 정의하는 방법보다 훨씬 쉽다.  
<br>

사용법에 대한 간단한 예를 살펴보자. 이 예는 공식문서에서 가져왔음을 밝힌다.

```python
# HTML code generating function

from contextlib import contextmanager

@contextmanager
def tag(name):
    print("<{}>".format(name))
    yield
    print("</{}>".format(name))

>>> with tag("h1"):
>>>     print("foo")

<h1>
foo
</h1>
```

아마 감이 오지 않았을까 싶다. 어떤 tag 이름을 적든 내용물에 입력한 태그를 씌울 것이다.  
주목할 점은 **yield**이다. 제너레이터 표현 방법인데 yield 뒤가 비어 있는 것은 익숙하지 않을 것이다.  
이것은 **with안 블록 또는 컨텍스트가 작성되는 함수의 yield에서 실행된다는 것을 의미한다.**  

또한 yield를 사용한다는 것은 이 함수가 제너레이터라는 것을 의미하며  
일반적으로 reentrant하지 않다.  

```python
# contextmanager used generator is not reentrant
from contextlib import contextmanager

def singleuse():
    print("Before")
    yield
    print("After")


>>> cm = singleuse()
>>> with cm:
...     pass

Before
After

>>> with cm:
...     pass

Traceback (most recent call last):
  ...
RuntimeError: generator didn't yield
```

reentrant한 contextmanager를 원한다면 공식문서를 자세히 읽어보자.~~(잘 모르겠다. ㅠㅠ)~~

<br><br>

이제는 좀 더 제대로 된 예제를 살펴보자.  
내장 [logging](https://docs.python.org/3/library/logging.html) 모듈을 사용한 예제로,  
프로그램에서 일정 수준의 디버깅 로그를 남기는데 특정 영역에서는 더 높은 수준의 로그를 넣고 싶다고 해보자.  
먼저 로깅 심각성 수준 두 개로 로그를 남기는 함수를 정의하자.  


```python
import logging


def my_function():
    logging.debug("Some debug data")
    logging.error("Error log here")
    logging.debug("Final debug data")

my_function()


>>>
Error log here
```

<br>

logging 모듈은 logger를 통해 원하는 순간에 로그를 남길 수 있는데  
로그의 수준이 상황마다 다 다를 것이고 기본 설정한 수준 이상이 되는 상황에서만  
로그를 남기도록 할 수 있다.(CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET 수준. 순서가 빠를수록 더 심각.)  
프로그램의 기본 로그 수준은 WARNING이고 함수를 실행하면 WARNING보다 수준이 더 높은 오류 메시지만 출력된다.  
contextmanager를 정의하면 이 함수의 로그 수준을 임시로 높일 수 있다.  
이 헬퍼 함수는 with 블록에서 코드를 실행하기 전에 로그 심각성 수준을 높이고 실행 후에는 다시 낮춘다.

```python
@contextmanager
def debug_logging(level):
    logger = logging.getLogger()  # 현재의 로거를 획득
    old_level = logger.getEffectiveLevel()  # 현재 로거의 수준을 획득
    logger.setLevel(level)  # 인자로 받은 수준으로 로거 수준 설정
    try:
        yield
    finally:
        logger.setLevel(old_level)  # 블록 실행 후 다시 원래 수준으로 재설정
```

앞서 말했듯이 yield 부분이 with 블록의 내용이 실행되는 지점이다.  
이 부분을 try/finally 부분으로 감쌈으로써   
**with 블록에서 일어나는 모든 예외를 yield 표현식이 다시 일으키므로
이 부분을 try/finally 부분으로 감쌈으로써 예외를 헬퍼 함수로 처리할 수 있다.**  


이제 같은 로깅 함수를 debug\_logging 컨텍스트에서 호출한다.  
이번에는 with 블록 안에 있는 디버그 메시지가 모두 화면에 출력되지만,  
바깥에서는 출력되지 않을 것이다.

```python
with debug_logging(logging.DEBUG):
    print("Inside: ")
    my_function()
print("After: ")
my_function


>>>
Inside:
Some debug dat
Error log here
Final debug data
After:
Error log here

# 로그 레벨을 낮출 with 블록 안에서만 로그가 모두 출력됨
```

<br><br>

## Part 2. with 타깃 사용하기

with 문에 전달되는 컨텍스트 매니저에서 객체를 반환할 수도 있다.  
이 객체는 복합문에 as 부분에 있는 지역 변수에 할당된다.  
이 기능을 이용하면 with 블록 안에 있는 코드에서 직접 컨텍스트와 상호작용할 수 있다.
앞서 봤던 파일 여닫는 코드가 그 예시이다.

```python
# 반환 객체를 fd라는 지역변수에 할당
with open('text.txt', 'r+') as fd:
    sentences = fd.read()
    for line in sentences:
        print(line)

    ...
```

함수에서 as 타깃에 값을 제공할 수 있게 하려면, 컨텍스트 매니저에서 yield를 사용하여  
값을 넘겨주기만 하면 된다. 예를 들어 다음은 Logger인스턴스를 가져와 심각성 수준을 설정한 후  
yield로 인스턴스를 as에 전달하도록 한 예다.

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

with 블록에서 로깅 심각성 수준을 충분히 낮게 설정해서 as 타깃으로 debug 같은 로깅 메서드를  
호출하면 출력이 나올 것이다. 기본 프로그램 로거의 기본 로깅 수준은 WARNGING이므로 logging 모듈을  
직접 사용하면 아무것도 출력되지 않는다.


```python
with log_level(logging.DEBUG, 'my_log') as logger:
    logger.debug("This is logging's instance logger and it's debug level")
    logging.debug("This is logging module level logger and it's WARNING level by default")

>>>
This is logging's instance logger and it's debug level
```

with 문이 종료한 후에 'my-log'라는 Logger의 디버그 로깅 메서드를 호출하면,  
기본 로깅 심각성 수준으로 되돌아간 뒤라서 아무것도 출력되지 않는다.  
물론 ERROR 수준의 로그는 항상 출력된다.


```python
logger = logging.getLogger('my-log')
logger.debug("Debug will not print")
logger.error("Error will print")

>>>
Error will print

# log_level 사용 예제에서 DEBUG 수준으로 설정했지만 finally 구문에서 다시 기존의 수준으로 복구됨.
```

<BR><BR>

**핵심정리**
* with 문을 이용하면 try/finally 불록의 로직을 재사용할 수 있고, 코드를 깔끔하게 만들 수 있다.
* 내장모듈 contextlib의 contextmanager 데코레이터를 이용하면 직접 작성한 함수를
with 문에서 쉽게 사용할 수 있다.
* 컨텍스트 매니저에서 넘겨준 값은 with 문의 as 부분에 할당된다. 컨텍스트 매니저에서 값을 반환하는
방법은 코드에서 특별한 컨텍스트에 직접 접근하려는 경우에 유용하다.
