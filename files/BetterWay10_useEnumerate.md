## Better Way 10. range보다는 enumerate를 사용하자

#### 41쪽

* Created : 2017/01/26
* Modified: 2019/05/06  

<br>

## 1. enumerate

파이썬을 처음 배울 때 for문을 배우게 된다. for문에서 **range**를 수없이 썼을 것이다.

```python
from random import randint

random_bit = 0
for i in range(64):
    if randint(0, 1):
        random_bit |= (1 << i)
# 이 코드는 정말 어썸.. 하나 배웠다.

print(random_bit)

>>> 13250328546979216565
```

또한 range를 통해 문자열의 리스트 같은 순회할 자료 구조가 있을 때는 직접 루프를 실행할 수도 있다.

```python
flavor_list = ['vanilla', 'chocolate', 'pecan', 'strawberry']

for flavor in flavor_list:
    print('{} is delicious'.format(flavor))

>>> vanilla is delicious
>>> chocolate is delicious
>>> pecan is delicious
>>> strawberry is delicious
```

<br>

좋다. 그런데 종종 리스트를 위와 같이 선회하는데 현재 아이템의 인덱스가 필요한 경우가 있다. 예를 들어 좋아하는 아이스크림의 순위를 출력하고 싶다고 하자.  

일반적인 방법은 **range**를 쓰는 것이다.  

```python
for i in range(len(flavor_list)):
    flavor = flavor_list[i]
    print('{index} : {flavor}'.format(
        index=i + 1,
        flavor=flavor))

>>> 1 : vanilla
>>> 2 : chocolate
>>> 3 : pecan
>>> 4 : strawberry
```

결과는 나왔는데.. 뭔가 께름칙하다. `range(len(flavor_list))`.. 너무 안 이쁘지 않은가??  

파이썬은 이런 상황을 처리하려고 내장 함수 **enumerate**를 제공한다. 이 함수는 지연 제너레이터(lazy generator)로 이터레이터를 감싼다.(lazy의 뜻은 나중에 포스트한다.)  

**이 제너레이터는 이터레이터에서(예를 들면 list iterator) 루프 인덱스와 다음 값을 한 쌍으로 가져와 넘겨준다.**  

직접 예를 보자.  

```python
for i, flavor in enumerate(flavor_list):
    print('{index} : {flavor}'.format(
        index=i + 1,
        flavor=flavor))

>>> 1 : vanilla
>>> 2 : chocolate
>>> 3 : pecan
>>> 4 : strawberry
```

이 예제에서 enumerate은 for문 안에서 기존 리스트의 원소(flavor)와 인덱스 i를 튜플로 반환하고 있다.  
인덱스와 아이템을 같이 받을 수 있어서 위와 같은 예제를 깔끔하게 해결할 수 있다.  

<br>

또한 enumerate에 추가 인자를 넣어서 인덱스의 시작값을 설정할 수도 있다.

```python
for i, flavor in enumerate(flavor_list, 1):
    print('{index}: {flavor}'.format(
        index=i,
        flavor=flavor))

# 동일한 결과가 나온다.
```

<br><br>

### 핵심 정리

* enumerate는 이터레이터를 순회화면서 이터레이터에서 각 아이템의 인덱스를 얻어오는 간결한 문법을 제공한다.
* range로 루프를 실행하고 시퀀스에 인덱스로 접근하기보다는 enumerate를 사용하는 게 좋다.
* enumerate에 두 번째 파라미터를 사용하면 세기 시작할 숫자를 지정할 수 있다.(기본 0)
