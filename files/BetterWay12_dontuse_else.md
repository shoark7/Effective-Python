## Better way 12. for와 while 루프 뒤에는 else 블록을 쓰지 말자

### 46쪽.
### 2017/01/31 작성

파이썬의 루프에는 대부분의 다른 프로그래밍 언어에는 없는 추가적인 기능이 있다.  
루프에서 반복되는 내부 블록 다음에 **else 블록을 쓸 수 있는 기능이다.**

```python
for i in range(3):
    print('Loop {}'.format(i))
else:
    print('Else block')
    
>>> Loop 0
>>> Loop 1
>>> Loop 2
>>> Else block
```
놀랍게도 else 블록은 루프가 종료되자마자 실행된다. 이걸 왜 else라고 부를까??  

if/else문에서나, try/except 문에서 else(except)는 이전 구문(if or try)이 실행되지 않으면 이 else 블록이 실행된다는 의미이다.  
이는 다른 프로그맹 언어에서도 마찬가지이다.  

그렇기에 파이썬을 처음 접하는 프로그래머들은 for/else의 else 부분이 '루프가 완료되지 않으면 이 블록을 실행한다'  
라고 짐작할 것이다.  실제로는 정확히 반대다.  
루프에서 break문을 사용해야 else 블록을 건너뛸 수 있다.

```python
for i in range(3):
    print('Loop {}'.format(i))
    if i == 1:
        break
else:
    print('Else block!')
    
>>> Loop 0
>>> Loop 1

# break문을 만나서 else 블록이 실행되지 않았다.
```
<br><BR>

다른 놀랄 점은 빈 시퀀스를 처리하는 루프 문에서도 else 블록이 즉시 실행된다는 것이다.

```python
for x in []:
    print('Never runs')

else:
    print('Not else block!')
    
>>> Not else block!
```

또 while 루프가 처음부터 거짓인 경우에도 실행된다.

```python
while False:
    print('Never runs')
else:
    print('While else block!')

>>> While else block!
```

<br><BR>

대관절 왜 이렇게 헷갈리게 만들어 놓았을까?  
이렇게 동작하는 이유는 루프 다음에 오는 else 블록은 루프로 뭔가를 검색할 때 유용하기 때문이다.  

예를 들어, 두 숫자가 서로소(coprime)인지를 판별한다고 해보자.  
이제 가능한 모든 공약수를 구하고 숫자를 테스트해보자.  
모든 옵션을 시도한 후에 루프가 끝난다.  
else 블록은 루프가 break을 만나지 않아서 숫자가 서로소일 때 실행된다.

```python
a = 4
b = 9

for i in range(2, min(a, b) + 1):
    print('Tesing' , i)
    if a % i == 0 and b % i == 0:
        print('Not prime')
        break
else:
    print('Coprime')

>>> Tesing 2
>>> Tesing 3
>>> Tesing 4
>>> Coprime
```

실제로는 이렇게 코드를 작성하면 안 된다.  

대신에 이런 계산을 하는 헬퍼 함수를 작성하는 것이 좋다.  
이런 헬퍼 함수는 두 가지 일반적인 스타일로 작성한다.

```python
# way 1. 조건을 찾으면 바로 반환하기

def coprime(a, b):
    for i in range(2, min(a, b) + 1):
        if a % i == 0 and b % i == 0:
            return False
    return True
```


```python
# way 2. 루프에서 찾으려는 대상을 찾았는지 알려주는 결과 변수를 사용하기

def coprime2(a, b):
    is_coprime = True
    for i in range(2, min(a, b) + 1):
        if a % i == 0 and b % i == 0:
            is_coprime = False
            break
    return is_coprime
```

이 일반적인 두 가지 방법을 사용하면 낯선 코드를 접하는 개발자들이 코드를 훨씬 쉽게 이해할 수 있다.  

else 블록을 사용한 표현의 장점이 나중에 여러분 자신을 비롯해 코드를 이해하려는 사람들이 받을 부담감보다 크지 않다.  
루프처럼 간단한 구조는 파이썬에서 따로 설명할 필요가 없어야 한다.  
그러므로 루프 다음에 오는 else 블록은 사용하지 말자.


## 핵심 정리

* 파이썬에는 for와 while 루프의 내부 블록 바로 뒤에 else 블록을 사용할 수 있게 하는 특별한 문법이 있다.
* 루프 본문이 break문을 만나지 않은 경우에만 루프 다음에 오는 else 블록이 실행된다.
* 루프 뒤에 else 블록을 사용하면 직관적이지 않고 혼동하기 쉬우니 사용하지 말아야 한다.
