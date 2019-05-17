## Better Way 20. 동적 기본 인수를 지정하려면 None과 docstring을 사용하자

#### 79쪽

* Created : 2016/10/08
* Modified: 2019/05/17  

<Br>

## 1. 함수에서 비정적 타입의 기본인자 사용의 문제점

앞선 장들에서 우리는 키워드 인자의 기본값으로 3, 1 같은 비정적(non-static) 타입만을 사용했다. 이때는 함수를 사용함에 있어서 섬세한 주의가 필요하다.  

예를 들어 이벤트 발생 시각을 포함해 로깅 메시지를 출력한다고 하자. 서버에 로그를 남길 때 로그 기록 시간은 같이 기록하기 마련이다. 일반적인 로그 함수에 기록될 시간은 함수가 호출되는 시간이지만 원할 경우에는 임의의 시간 기록이 가능하도록 작성한다고 하자. 아마 다음과 같을 것이다.


```python
import datetime
import time


# Use Python 3.6 boy
def log(message, when=datetime.datetime.now()):
    print(f"{when}: {message}")
```

메시지와 시간을 기록하는 로그 함수를 만들었다. 로그 메시지는 일반적으로 호출된 그 시간을 기록하기 때문에 19장에서 배운대로 키워드 인자를 통해 _when_ 의 기본값을 만들었다. 잘 작동하는지 볼까?


```python
# 1. Test 1
log("Greetings!")

# 2. Test 2 after sleep 0.1 sec
time.sleep(0.1)
log("Greetings again")

2019-05-17 12:15:14.811373: Greetings!
2019-05-17 12:15:14.811373: Greetings again
```

첫 번째 로그 함수를 호출한 뒤 _time.sleep_ 으로 0.1초 정도 뒤에 다시 호출했다. 당연히 두 로그에 기록된 시간이 다르리라 예상할 수 있다. 그런데 이상하게도 두 함수의 시간이 동일하다. 참 기묘한 일인데 왜 그럴까?

**_now_ 함수는 함수 호출이 아닌 함수 정의식에서 호출되었다. 함수 정의는 프로그램이 실행될 때 한 번만 진행되므로 _when_ 은 처음 함수가 정의될 때의 시간으로 고정된 것이다.** 결과적으로 '3' 같은 정적값을 준 것과 큰 차이가 없게 되었다. 그래서 비정적 타입을 기본 인자로 쓸 때 주의해야 한다.


<br>

## 2. 해결책

이런 상황에서 의도한 대로 결과가 나오게 하려면 **기본값을 _None_ 으로 설정하고 docstring으로 실제 동작을 문서화하는 게 관례다.** 코드에서 인수 값으로 _None_ 이 나타나면 알맞은 기본값을 할당하면 된다.


```python
def log(message, when=None):
    """Log a message with a timestamp

    :input:
        message: Message to print
	when: datetime of when the message occurred.
	      Defaults to the present time.
    """
    if when is None:
        when = datetime.datetime.now()
    print(f"{when}: {message}")



log("Greetings!")
time.sleep(0.1)
log("Greetings again")


2019-05-17 12:27:54.804982: Greetings!
2019-05-17 12:27:54.906290: Greetings again
```

이제 의도한 대로 동작하고 있다.

<br>

## 3. 추가 예제

**기본 인자로 _None_ 을 사용하는 방법은 인자가 Mutable할 때 특히 중요하다.** 예를 들어 JSON 데이터로 인코드된 값을 로드한다고 해보자. 데이터 디코딩이 어떤 이유로든 실패하면 기본값으로 빈 딕셔너리를 반환하려고 한다. 다음과 같은 방법을 써볼 수 있겠다.

```python
import json


def decode(data, default={}):
    try:
        return json.loads(data)
    except ValueError:
        return default
```

이 코드는 아까의 로그 예제와 같은 문제가 있다. **기본 인자값은 모듈이 로드될 때 딱 한 번만 평가되므로, 기본값으로 설정한 딕셔너리를 모든 decode 호출에서 공유한다.** 이는 더 심각한 문제를 낳는다.

```python
foo = decode('bad data')
foo['stuff'] = 3

bar = decode('So do I!')
bar['eggs'] = 5

>>> print('foo:', foo)
>>> print('bar:', bar)


foo: {'stuff': 3, 'eggs': 5}
bar: {'stuff': 3, 'eggs': 5}
```

이 예제에서는 당연히 _foo_, _bar_ 각각 단일 키와 값을 담은 서로 다른 딕셔너리를 가졌으리라 예상했을 것이다. 하지만 **두 함수 모두 함수 정의 시에 설정된 _default_ 딕셔너리를 공유하고, 딕셔너리는 값이 변할 수 있기 때문에, 다시 말해 Mutable하기 때문에 하나가 수정되면 다른 하나도 수정되는 것처럼 보인다.** 실제로 반환된 딕셔너리는 같은 값이다.


```python
assert foo is bar
```

이때에도 _default_ 값을 _dict_ 가 아닌 _None_ 으로 초기화하고 함수의 docstring에 동작을 문서화해 이 문제를 고친다.

```python
import json


def decode(data, default=None):
    """Load JSON data from a string

    :input:
        data: JSON string to parse.
	default: Value to return if decoding fails. Defaults to an empty dict.
    """
    if default is None:
        default = {}

    try:
        return json.loads(data)
    except ValueError:
        return default
```

이제 앞서 나온 테스트 코드들이 예상한 대로 동작할 것이다.


```python
foo = decode('bad data')
foo['stuff'] = 3

bar = decode('So do I!')
bar['eggs'] = 5

>>> print('foo:', foo)
>>> print('bar:', bar)


foo: {'stuff': 3}
bar: {'eggs': 5}
```

이렇듯 키워드 인자의 기본값을 비정적 타입으로 줄 때는 조심해야 한다.

<br>


## 4. 핵심 정리

* 기반 인자는 모듈 로드 시점에 함수 정의 과정에서 딱 한 번만 평가된다. 그래서 (`{}`나 `[]`와 같은) 동적 값에는 이상하게 동작하는 원인이 된다.
* 값이 동적인 키워드 인자는 기본값으로 _None_ 을 사용하자. 그러고 나서 함수의 docstring에 실제 기본 동작을 문서화하자.
