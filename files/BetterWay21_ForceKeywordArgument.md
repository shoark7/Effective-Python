## Better Way 21. 키워드 전용 인수로 명료성을 강요하자

#### 83쪽

* Created : 2016/10/27
* Modified: 2019/05/20  

<Br>


## 1. 일반 키워드 인자 사용의 맹점

키워드로 인수를 넘기는 방법은 파이썬 함수의 강력한 기능이다. 이는 [19장](https://github.com/shoark7/Effective-Python/blob/master/files/BetterWay19_KeywordArg.md)에서 확인한 바 있다. 키워드 인자의 유연성 덕분에 쓰임새가 분명하게 코드를 작성할 수 있다.

예를 들어 어떤 숫자를 다른 숫자로 나눈다고 하자. 이때 특별한 경우를 상정하자. 때로는 0을 분모로 할 때 _ZeroDivisionError_ 대신 무한대를 반환하고 싶을 수도 있고, 어떨 때는 값이 너무 커질 때 반환되는 _OverflowError_ 대신 0을 반환하고 싶을 수도 있다.  

이를 함수로 짜보자.


```python
def safe_division(n, d, ignore_overflow, ignore_zero_division):
    try:
        return n / d
    except OverflowError:
        if ignore_overflow:
            return 0
        else:
            raise
    except ZeroDivisionError:
        if ignore_zero_division:
            return float('inf')
        else:
            raise
```

try 문이 두 개 쓰여서 복잡해보이지만 사용법은 간단하다. 단순히 분자를 분모로 나누되, 지정한 에러가 발생하면 앞서 정의한 대로 문제를 처리한다.

다음 호출은 나눗셈에서 일어나는 float 오버플로우를 무시하고 0을 반환한다.


```python
result = safe_division(1, 10**500, True, False)
print(result)

0.0
```

다음은 0으로 나누면 일어나는 오류를 무시하고 무한대 값을 반환한다.


```python
result = safe_division(1, 0, False, True)
print(result)

inf
```


**문제는 예외 무시 동작을 제어하는 두 bool 인자의 위치를 혼동하기 쉽고 이해하기도 힘들다는 것이다.** 이 때문에 찾기 어려운 버그가 쉬이 발생할 수 있다. 이런 코드의 가독성을 높이는 한 가지 방법은 역시 키워드 인자를 사용하는 것이다.

```python
def safe_division_b(n, d, ignore_overflow=False, ignore_zero_division=False):
    ...
```

함수를 호출하는 쪽에서는 다음과 같이 사용하리라 기대할 수 있다.

```python
result = safe_division_b(1, 0, ignore_zero_division=True)
```

이것도 괜찮은 방법이지만 완벽하지는 않는데, **이런 키워드 인자가 선택적인 동작이라서 함수를 호출하는 쪽에서 키워드 인자로 의도를 명확하게 드러내라고 강제할 방법이 없다.** 새로 정의한 함수 또한 여전히 위치 인자를 사용하는 이전 방식으로 호출할 수 있다.


```python
result = safe_division_b(1, 0, True, False)
```

<br>

## 2. 해결책


이처럼 인자가 많은 복잡한 함수를 작성할 때는 호출하는 쪽에서 의도를 명확히 드러내도록 요구하는 것이 낫다. **파이썬 3에서는인자를  키워드 전용 인수(keyword-only argument)로 정의해서 의도를 명확히 드려내도록 요구할 수 있다.** 키워드 전용 인수는 키워드로만 넘길 뿐, 위치로는 절대 넘길 수 없다.

사용법은 간단한데, 다음과 같다.

```python
def safe_division_c(n, d, *, 
                    ignore_overflow=False, ignore_zero_division=False):
    ...
```

**이제 '\*' 뒤에 있는 인수들은 위치 인자로 보내면 동작하지 않는다.** 설정된 기본값만 쓰든지, 아니면 함수에 명시적인 키워드 인자를 건네야 한다.

```python
safe_division_c(1, 0, True)

TypeError: safe_division_c() takes 2 positional arguments but 3 were given
```

일반적인 키워드 인자처럼 활용하면 전혀 문제가 없다. **함수에 관리해야 할 인자가 많거나, 인자 자체의 의미가 중요해서 그 의미를 사용자가 명확히 인지해야 할 경우, 인자를 키워드 인자로 강제하는 방법도 생각해봄직 하다.**

<br>

## 3. 핵심 정리

* 키워드 인자는 함수 호출의 의도를 더 명확하게 해준다.
* bool 플래그를 여러 개 받는 함수처럼 헷갈리기 쉬운 함수를 호출할 때 키워드 인자를 넘기게 하려면 키워드 전용 인자를 사용하자.
* 파이썬 3에서는 함수의 키워드 전용 인자 문법을 명시적으로 지원한다. 파이썬 2는 지원하지 않는다.
