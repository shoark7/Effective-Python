## Better Way 51. 루트 Exception을 정의해서 API로부터 호출자를 보호하자

#### 262쪽

* Created : 2019/07/02
* Modified: 2019/07/02

<br>

## 1. 모듈 전용 Error를 정의한다는 것

모듈의 API를 정의할 때 여러분이 던지는 예외는 인터페이스의 일부로 정의한 함수와 클래스만이다. 파이썬은 언어와 표준 라이브러리용 내장 예외 계층을 갖추고 있다. 오류를 보고할 때 자신만의 새 탕비을 정의하는 대신 내장 예외 타입을 사용할 가능성이 크다. 예를 들어, 함수에 올바르지 않은 파라미터가 넘어오면 ValueError 예외를 일으킬 수 있다.

```python
def determine_weight(volume, density):
    if density <= 0:
        raise ValueError("밀도는 0 이하일 수 없습니다.")
```

이런 상황에서 몇몇 경우에는 ValueError를 ㅅ 아요하는 것을 이해할 수 있지만 **API용으로는 자신만의 예외 계층을 정의하는 방법이 더 강력하다.** 예외 계층을 정의하려면 모듈 내에서 루트 Exception을 제공하면 된다. 그런 다음 해당 모듈에서 일어나는 다른 예외가 모두 루트 예외로부터 상속받게 한다.

```python
class Error(Exception):
    """Base exception class for this module."""
    pass

class InvalidDensityError(Error):
    """There was a problem with a provided density value."""
    pass
```

알다시피 **_Exception_ 은 파이썬의 모든 내장 예외의 최상위 부모 클래스다.** 오류 세계에서의 _object_ 라고 할 수 있다. 이 예외를 상속하는 _Error_ 클래스를 생성함으로써 현재 작성하는 모듈 또는 프레임워크만을 위한 최상위 에러 클래스를 정의했다.

모듈에 루트 예외를 두면 API 사용자들이 목적을 두고 일으킨 모든 예외를 잡아낼 수 있다. 예를 들어 API 사용자는 루트 예외를 잡아내는 try / except 문으로 함수를 호출할 수 있다.

```python
def determine_weight(volume, density):
    if density <= 0:
        raise InvalidDensityError("밀도는 0 이하일 수 없습니다.")
        # 에러 변경
```


```python
try:
    weight = my_module.determine_weight(1, -1)
except my_module.Error as e:
    print("Unexpected error:", e)


Unexpected error: 밀도는 0 이하일 수 없습니다.
```

이 try / except는 API의 예외가 너무 빨리 멀리 퍼져나가서 호출하는 프로그램을 중단하는 일을 막는다. 이 구문은 호출하는 코드를 API로부터 보호한다. 이런 보호는 세 가지 유용한 효과를 낸다.


1. 루트 예외가 있으면 호출자가 API를 사용할 때 문제점을 이해할 수 있다.
  - 호출자가 API를 올바르게 사용한다면 개발자가 의도적으로 일으킨 다양한 예외를 잡아낼 수 있어야 한다.
  - 그러한 예외를 처리할 수 없다면 개발자가 작성한 모듈의 루트 예외를 잡아서 보호하는 except 블록까지 전파된다. 이 except 블록은 API 사용자가 예외를 주목하게 하여 해당 예외 타입을 적절히 처리하는 코드를 추가하게 만든다.

```python
try:
    weight = my_module.determine_weight(1, -1)
except my_module.InvalidDensityError:
    weight = 0
except my_module.Error as e:
    print("Unexpected error:", e)

# 에러의 계층구조를 확인
```

2. API 모듈의 코드에 있는 버그를 찾는 데 도움이 된다.
  - 코드에서 모듈 계층 안에 정의한 예외만 의도적으로 일으킨다면, 해당 모듈에서 일어난 다른 타입의 예외(예를 들어 내장 _Exception_)는 모두 의도하지 않은 것이 틀림없다. 이런 예외가 곧 버그다.

try / except 문을 사용한다고 해서 API 모듈에 있는 모든 버그로부터 사용자들을 보호하지는 못한다. **API 사용자를 보호하려면 호출자가 파이썬의 _Exception_ 기반 클래스를 잡아내는 다른 except 블록을 추가해야 한다.**

```python
try:
    weight = my_module.determine_weight(1, -1)
except my_module.InvalidDensityError:
    weight = 0
except my_module.Error as e:
    print("Unexpected error:", e)
except Exception as e: # 예상 못한 예외를 모두 잡는다.
    print('Bug in the code:', e)
    raise
```

3. 마지막 효과는 API의 미래를 대비할 수 있다는 것이다.
  - 시간이 지나 특정 환경에서 더 구체적인 예외를 제공하려고 API를 확장할 수도 있다. 예를 들어 밀도를 음수로 넘기는 오류 상황을 알리는 _Exception_ 서브클래스를 추가할 수도 있다.

```python
class NegativeDensityError(InvalidDensityError):
    """Provided density value was negative."""

def determine_weight(volume, density):
    if density <= 0:
        raise NegativeDensityError("밀도는 0 이하일 수 없습니다.")
```

밀도값이 부적절할 때 반환하는 에러를 더 확장해서(상속해서) _InvalidDensityError_ 음수의 입력에 대응하는 _NegativeDensityError_ 를 만들었다. 그리고 *determine\_weight* 함수가 밀도값이 0 이하일 때 새로 만든 에러를 반환하도록 했다.

이때, **이전에 작성한 try / excpet 문에서 _InvalidDensityError_ 에러는  _NegativeDensityError_ 의 부모 클래스이기 때문에 문제없이 에러를 잡아내므로 이전과 똑같이 동작한다.** 나중에 호출자가 새 예외 타입을 특별한 경우로 처리하도록 결정하고 그에 따라 동작을 변경할 수 있다.

```python
try:
    weight = my_module.determine_weight(1, -1)
except my_module.NegativeDensityError as e:
    raise ValueError('Must supply positive density') from e
exept my_module.InvalidDensityError:
    weight = 0
except my_module.Error as e:
    print("Bug in the code:", e)
except Exception as e:
    print("But in the API code:", e)
    raise
```

마지막 두 줄에 집중해보자. *my\_module.Error* 까지는 개발자 입장에서 모두 예측하고 정의한 에러이기 때문에 사용자 코드에 문제가 있다고 이해할 수 있다.  

하지만 마지막 _Exception_ 에서는 개발자가 의도 못한 에러이기 때문에 개발자의 실수라고 봐야하고 이는 곧 API의 버그를 의미한다.

<br>

`확장`의 강력함은 더 추가할 수 있다. 루트 예외 바로 아래에 더 많은 예외를 제공하여 API의 미래를 대비할 수 있다. 예를 들어 무게, 부피, 밀도 계산과 관련이 있는 오류 집합을 각각 만들고 싶다고 하자.


```python
# my_module.py
class WeightError(Error):
    """Base class for weight calculation erros."""
    pass

class VolumeError(Error):
    """Base class for volume calculation erros."""
    pass

class DensitytError(Error):
    """Base class for density calculation erros."""
    pass
```

**구체적인 예외는 이런 일반적인 예외로부터 상속해서 만든다.** 각 중간 예외는 루트 예외처럼 동작한다. 이 방법을 이용하면 많은 기능을 기반으로 한 API 코드로부터 호출하는 코드를 쉽게 분리할 수 있다. 이 방법이 모든 호출자가 매우 구체적인 Exception 서브클래스를 각각 캐치하는 방법보다 훨씬 낫다.

<br>

## 2. 핵심 정리

* 작성 중인 모듈에 루트 예외를 정의하면 API로부터 API 사용자를 보호할 수 있다.
* 모듈을 위해 정의한 루트 예외를 잡으면 API를 사용하는 코드에 숨은 버그를 찾는 데 도움이 될 수 있다.
* 파이썬 Exception 기반 클래스를 잡으면 API 구현에 있는 버그를 찾는 데 도움이 될 수 있다.
* 중간 루트 예외를 이용하면 API를 사용하는 코드에 영향을 주지 않고 나중에 더 구체적인 예외를 추가할 수 있다.
