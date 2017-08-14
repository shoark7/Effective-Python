# Better way 43. functools.wraps로 함수 데코레이터를 정의하자


#### 216쪽
#### 2017/08/14 작성

파이썬에는 함수에 적용할 수 있는 데코레이터 문법이 있다.  
(이에 대한 설명은 생략한다. 데코레이터에 대한 개념 부족 시 다른 포스트를 참고한다.)  
데코레이터는 감싸고 있는 함수를 호출하기 전후에 추가로 코드를 실행할 수 있게 한다.  
이는 활용이 무궁무진한데, 입력, 반환값에 접근하는 등 여러 상황에 유용하다.  

두 가지 데코레이터 활용예제를 제시한다.  
* 1. 함수를 호출할 때 인수와 반환 값을 출력한다. 이는 스택 디버깅에 도움이 된다.
* 2. 함수의 실행시간을 잰다. 이는 여러 함수의 유용성을 판단하는 데 도움이 된다.
<br>

```python
# 1. 함수 호출 시 인수와 반환 값을 출력
def trace(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
	print("{}({}, {}) -> {}".format(func.__name__, args, kwargs, result))
	return result
    return wrapper


# 2. 함수 호출 시 총 실행시간 출력(개인적으로 유용하게 사용한다.)
def get_execution_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()

        print('-' * 40)
        print('Execution time : ', end - start)
	return result
    return wrapper
```

<br>
위는 데코레이터 함수를 정의하는 몇 가지 예다.
잘 알다시피 '@' 기호로 데코레이터를 함수에 적용하는데  
**감싸는 함수를 인수로 하여 데코레이터를 호출한 후 반환 값을 원래 이름 코드에 할당한다**  
<br>

```python
# 1. trace를 통해 재귀함수의 스택 추적

@trace
def fibonacci(n):
    """n번 째 피보나치 수를 반환한다."""
    if n in (0, 1):
        return n
    return fibonacci(n - 2) + fibonacci(n - 1)
```

<br>
위와 같이 감싸면 피보나치 수열을 구하고 그 스택 순서를 쫓을 수 있다. 
<br>

```python
fibonacci(4)

>>>
Args : (1,), kwargs: {} -> results: 1
Args : (0,), kwargs: {} -> results: 0
Args : (2,), kwargs: {} -> results: 1
Args : (1,), kwargs: {} -> results: 1
Args : (3,), kwargs: {} -> results: 2
Args : (1,), kwargs: {} -> results: 1
Args : (0,), kwargs: {} -> results: 0
Args : (2,), kwargs: {} -> results: 1
Args : (4,), kwargs: {} -> results: 3
```

<br><br>
이 코드는 잘 작동하지만 의도하지 않은 부작용을 일으킨다.  
데코레이터에서 반환한 값, 그러니까 함수의 이름이 fibonacci가 아니다.

```python
print(fibonacci)


>>>
<function my_module.trace_results.<locals>.wrapper>
```
그러니까 함수 이름이 wrapper인 것이다.  
문제의 원인은 어렵지 않은데 데코레이터의 작동방식에서 알 수 있듯이  
함수를 작성 후 데코레이터를 씌우면 데코레이터가 반환한 wrapper 함수가
함수의 이름이 되고 fibonacci라는 이름이 할당된 것이다.

이 동작은 디버거나 객체 직렬화처럼 객체 내부를 조사하는 도구를 사용할 때  
문제가 될 수 있다.  

좀 더 살펴보면 데코레이터를 적용한 fibonacci 함수에는 help 내장 함수가 쓸모가 없다.
<br>

```python
help(fibonacci)

>>>
Help on function wrapper in module my_module:

wrapper(*args, **kwargs)


# fibonacci 함수를 정의했는데 wrapper에 대한 도움말을 제시함.
```
<br>
<br>
<br>


해결책은 내장 모듈 functools의 **wraps** 헬퍼 함수를 사용하는 것이다.  
이 함수는 데코레이터를 작성하는 데 이용하는 데코레이터로,  
**내부 함수에 있는 중요 메타데이터가 모두 외부함수로 복사된다.**


<br>
```python
def trace_results(func):                                                        
    @wraps(func)                                                                
    def wrapper(*args, **kwargs):                                               
    ...
```
사용법은 흔히 wrapper라고 이름 짓는 반환함수에 wraps를 데코레이터로 씌우는 것이다.  
이제 help 함수를 실행하면 우리가 원한 결과를 얻을 수 있다.
<br>

```python
help(fibonacci)

>>>
Help on function fibonacci in module __main__:

fibonacci(n)
    n번 째 피보나치 수를 반환한다.

```

<br><br>
help를 호출한 예는 데코레이터가 어떤 식으로 미묘한 문제를 일으키는지  
보여주는 사례 중 하나일 뿐이다. 파이선 함수에는  
여러 표준 속성(\_\_name\_\_, \_\_module\_\_ 등)이 있으며,  
언어에서 함수들의 인터페이스를 유지하려면 이 속성들을 반드시 보호해야 한다.  
wraps를 사용하면 언제나 올바른 동작을 얻을 수 있다.
<br><br>


## 핵심정리
* 데코레이터는 런타임에 한 함수로 다른 함수를 수정할 수 있게 해주는 파이썬 문법이다.  
* 데코레이터를 사용하면 디버거와 같이 객체 내부를 조사하는 도구가 이상하게 동작할 수도 있다.
* 직접 데코레이터를 정의할 때 이런 문제를 피하려면 functools의 wraps를 사용하자.
