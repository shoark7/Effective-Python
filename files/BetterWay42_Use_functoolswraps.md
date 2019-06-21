## Better Way 42. functools.wraps로 함수 데코레이터를 정의하자

#### 216쪽

* Created : 2017/08/14
* Modified: 2019/06/21

<br>


## 1. 데코레이터 사용의 문제점

파이썬에는 함수에 적용할 수 있는 데코레이터(decorator)라는 특별한 문법이 있다.(이에 대한 설명은 생략한다. 데코레이터에 대한 개념 부족 시 다른 포스트를 참고한다.) 데코레이터는 감싸고 있는 함수를 호출하기 전후에 추가로 코드를 실행할 수 있게 한다. 이는 활용이 무궁무진한데, 입력, 반환값에 접근, 디버깅, 시맨틱 강조 등 등 여러 상황에 유용하다.  

예를 들어 함수를 호출할 때 인수와 반환 값을 출력하고 싶다고 하자. 특히, 재귀호출에서 함수 호출의 스택을 디버깅할 때 도움이 된다. 그럼 이런 데코레이터를 정의해보자.


```python
# 1. 함수 호출 시 인수와 반환 값을 출력
def trace(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print("{}({}, {}) -> {}".format(func.__name__, args, kwargs, result))
        return result
    return wrapper
```

잘 알다시피 '@' 기호로 데코레이터를 함수에 적용한다. 데코레이터를 적용할 함수로 유명한 피보나치 함수를 만들어보자.

**감싸는 함수를 인수로 하여 데코레이터를 호출한 후 반환 값을 원래 이름 코드에 할당한다**  

```python
# 1. trace를 통해 재귀함수의 스택 추적

@trace
def fibonacci(n):
    """n번 째 피보나치 수를 반환한다."""
    if n in (0, 1):
        return n
    return fibonacci(n - 2) + fibonacci(n - 1)
```

**`@` 기호는 감싸고 있는 함수를 인수로 사용하여 해당 데코레이터를 호출한 후 반환값을 같은 스코프에 있는 원래 이름에 할당하는 코드에 상응한다.** 즉, 위의 데코레이터를 사용한 함수식은 다음 코드와 동일하다.

```python
fibonacci = trace(fibonacci)
```

이 데코레이터 함수를 호출하면 fibonacci 실행 전후에 wrapper 코드를 실행하여 재귀 스택의 각 단계마다 인수와 반환 값을 출력한다.

```python
fibonacci(3)

fibonacci((1,), {}) -> 1
fibonacci((0,), {}) -> 0
fibonacci((1,), {}) -> 1
fibonacci((2,), {}) -> 1
fibonacci((3,), {}) -> 2
```

3번째 피보나치 수를 구하자 각 재귀호출의 결과가 한 줄씩 차치하며 출력되는 것을 확인할 수 있다.

<br>

이 코드는 잘 작동하지만 의도하지 않은 부작용을 일으킨다. **데코레이터에서 반환한 값, 그러니까 함수의 이름이 fibonacci가 아니다.**

```python
print(fibonacci)

<function trace.<locals>.wrapper at 0x7fdb458b3400>
```

그러니까 **'fibonacci'라는 변수명에 할당된 함수 이름이 실제로는 'wrapper'인 것이다. 문제의 원인은 어렵지 않은데, 데코레이터의 작동방식에서 알 수 있듯이  함수를 작성 후 데코레이터를 씌우면 데코레이터가 반환한 wrapper 함수가 함수의 이름이 되기 때문이다.**

이 동작은 디버거나 객체 직렬화처럼 객체 내부를 조사하는 도구를 사용할 때  
문제가 될 수 있다.  

좀더 살펴보면 데코레이터를 적용한 fibonacci 함수에는 help 내장 함수가 쓸모가 없다.

<br>

```python
help(fibonacci)

Help on function wrapper in module __main__:

wrapper(*args, **kwargs)

# 'fibonacci'에 대한 사용설명서에서  wrapper에 대한 도움말을 제시함.
# 사용자는 멘붕;
```

<br>


## 2. 해결책

**해결책은 내장 모듈 functools의 wraps 헬퍼 함수를 사용하는 것이다.** 이 함수는 데코레이터를 작성하는 데 이용하는 데코레이터로, **이 함수를 wrapper 함수에 적용하면 내부 함수에 있는 중요 메타데이터가 모두 외부함수로 복사된다.**


```python
from functools import wraps

def trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print("{}({}, {}) -> {}".format(func.__name__, args, kwargs, result))
        return result
    return wrapper
```

사용법은 흔히 wrapper라고 이름 짓는 반환함수에 wraps를 데코레이터로 씌우는 것이다. 이제 help 함수를 실행하면 우리가 원한 결과를 얻을 수 있다.

```python
help(fibonacci)


Help on function fibonacci in module __main__:

fibonacci(n)
    n번 째 피보나치 수를 반환한다.
```

help를 호출한 예는 데코레이터가 어떤 식으로 미묘한 문제를 일으키는지 보여주는 사례 중 하나일 뿐이다. 파이선 함수에는 여러 표준 속성(\_\_name\_\_, \_\_module\_\_ 등)이 있으며, 언어에서 함수들의 인터페이스를 유지하려면 이 속성들을 반드시 보호해야 한다. 이때 wraps를 사용하면 언제나 올바른 동작을 얻을 수 있다.


<br>

## 3. 핵심 정리

* 데코레이터는 런타임에 한 함수로 다른 함수를 수정할 수 있게 해주는 파이썬 문법이다.
* 데코레이터를 사용하면 디버거와 같이 객체 내부를 조사하는 도구가 이상하게 동작할 수도 있다.
* 직접 데코레이터를 정의할 때 이런 문제를 피하려면 내장 모듈 functools의 wraps 데코레이터를 이용하자.
