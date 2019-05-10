## Better Way 14. _None_ 을 반환하기보다는 예외를 일으키자

#### 54쪽

* Created : 2017/02/02
* Modified: 2019/05/09  

<br>


## 1. 함수에서 _None_ 을 반환할 때의 문제점.

파이썬 프로그래머들은 유틸리티 함수를 작성할 때 반환 값 _None_ 에 특별한 의미를 부여하는 경향이 있다. 어떤 경우에는 일리 있어 보인다. 예를 들어 어떤 숫자를 다른 숫자로 나누는 헬퍼 함수를 생각해보자. 0으로 나누는 경우에는 결과가 정의되어 있지 않기 때문에 _None_ 을 반환하는 게 자연스러워 보인다.  

```python
def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None

# 이 함수는 다음과 같이 활용해볼 수 있다.
result = divide(x, y)
if result is None:
    print('Invalid inputs')
```

위와 같이 활용한다면 큰 문제는 없어 보인다.  
그런데 같은 활용식을 다음과 같이 써보면 어떨까?  

```python
result = divide(x, y)
if not result:
    print('Invalid inputs')
```

`if not` 같은 식도 파이썬에서는 자주 사용되는 조건식이다. 이 함수를 사용하는 프로그래머들이 충분히 사용하리라 예상해볼 수 있다.  

그렇지만 이 식은 문제가 있는데, 만약 분자가 0이라면, _result_ 는 0이 되고 그러면 조건식에서는 거짓으로 판단된다는 것이다.  파이썬에서는 **_None_, 빈 문자열, 빈 리스트, 0 등이 모두 조건식에서 거짓으로 판단된다.** 결국 **나눈 값이 단순히 0인데도 결과가 0으로 나눴을 때의 예외처리를 한 것처럼 작동할 수 있다.** 이렇기 때문에 함수에서 _None_ 을 반환하면 오류가 일어나기 쉽다.  이런 오류가 일어나는 상황을 줄이는 방법은 크게 두 가지가 있다.

<br>


## 2. 해결 방법

### 2.1. 반환 값을 두개로 나눠서 튜플에 담는다.

튜플의 첫 번째 부분은 작업이 성공했는지 실패했는지를 알려준다. 두 번째 부분은 계산된 실제 결과다.  

```python
def divide(a, b):
    try:
        return True, a / b	     # 튜플로 결과를 반환
    except ZeroDivisionError:
        return False, None   # 튜플로 결과를 반환

success, result = divide(x, y)
if not success:
    print('Invalid inputs')
```

이 함수를 호출하는 쪽에서는 튜플을 풀어야 한다. 따라서 나눗셈의 결과만 얻을 게 아니라 튜플에 들어 있는 상태(_success_) 부분까지 고려해야 한다.  

이 방법의 문제는 호출자가 파이썬에서 사용하지 않을 변수에 붙이는 관례인 밑줄 변수를 사용해서, 튜플의 첫 번째 부분을 쉽게 무시할 수 있다는 점이다.  

얼핏 보면 이 작성법이 잘못된 것 같지 않지만 결과는 그냥 _None_ 을 반환하는 것만큼 나쁘다.  

```python
_, result = divide(x, y)
if not result:
    print('Invalid results')
```

언제나 내가 만든 코드, 유탈리티 함수 등은 다른 사람들이 쓸 수도 있음을 염두에 둬야 한다.

<br>

### 2.2. 결코 _None_ 을 반환하지 않는다.

대신 **호출하는 쪽에 예외를 일으켜서 호출하는 쪽에서 그 예외를 처리하게 한다.** 여기서는 호출하는 쪽에 입력값이 잘못됐음을 알리려고 _ZeroDivisonError_ 을 _ValueError_ 로 변경했다.

```python
def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError as e:
        raise ValueError('Invalid inputs') from e
```

이제 호출하는 쪽에서는 잘못된 입력에 대한 예외를 처리해야 한다. 호출하는 쪽에서는 더는 함수의 반환 값을 조건식으로 검사할 필요가 없다. 함수가 예외를 일으키지 않았다면 반환 값은 문제가 없다. 예외를 처리하는 코드는 깔끔해진다.

```python
x, y = 5, 2

try:
    result = divide(x, y)
except ValueError:
    print('Invalid inputs')
else:
    print('Result is {:.2f}'.format(result))
    
>>> Result is 2.50
```

<br>

## 3. 부록 

위와 같은 식의 장점이 무엇일지 더 고민해보았다. 저 _divide_ 함수는 _ZeroDivisionError_ 말고도 다른 에러도 출력할 수 있는데,  가령 `5 / '2'`같이 나누면 _TypeError_ 가 발생할 것이다.  

_divide_ 함수에서 만약 _TypeError_ 까지 잡아서 같이 _ValueError_ 로 출력한다면, **호출하는 쪽(나일 수도, 다른 사람일 수도 있다)은 오류 메시지가 서로 다른 _ValueError_ 하나만 처리하면 된다.** 편의성이 증대되는 것.

<br>

## 4. 핵심 정리

* 특별한 의미를 나타내기 위해 _None_ 을 반환하는 함수가 오류를 일으키기 쉬운 이유는 _None_ 이나 다른 값(예를 들어 0)이 조건식에서 _False_ 로 평가되기 때문이다.
* 특별한 상황을 알릴 때 _None_ 을 반환하는 대신에 예외를 일으키자. 문서화가 되어 있다면 호출하는 코드에서 예외를 적절하게 처리할 것이라고 기대할 수 있다.
