## Better Way 11. 이터레이터를 병렬로 처리하려면 zip을 사용하자

### 43쪽
### 2017/01/30 작성

### Part 1.
파이썬에서 관련 객체로 구성된 리스트를 많이 사용한다는 사실은 쉽게 알 수 있다.  
리스트 컴프리헨션을 사용하면 소스 리스트에 표현식을 적용하여 파생 리스트(derived list)를 쉽게 얻을 수 있다.  

```python
names = ['Park', 'Lee', 'Kim']
letters = [len(name) for name in names]
```

파생 리스트의 아이템과 소스 리스트의 아이템은 서로 인덱스로 연관되어 있다.  
따라서 두 리스트를 병렬로 순회하려면 소스 리스트인 `names`의 길이만큼 순회하면 된다.

```python
longest_name = None
max_letters = 0

for i in range(len(names)):
    count = letters[i]
    if count > max_letters:
        longest_name = names[i]
        max_letters = count

print(longest_name)
```

무난한 루프이지만 별로 아름답지 않다.  
_names_와 _letters_를 인덱스로 접근하면 코드를 읽기 어려워진다.  
루프의 인덱스 _i_로 배열에 접근하는 동작이 두 번 일어난다.  
_enumerate_를 사용하면 문제점을 약간 개선할 수 있지만 여전히 완벽하지는 않다.

```python
for i, name in enumerate(names):
    count = letters[i]
    if count > max_letters:
        longest_name = name
        max_letters = count
```

파이썬은 위 코드를 좀 더 명료하게 하는 내장 함수 **_zip_**을 제공한다.  
파이썬 3에서 _zip_은 지연 제너레이터(lazy generator)로 이터러블 두 개 이상을 감싼다.  
_zip_ 제너레이터를 사용한 코드는 다중 리스트에서 인덱스로 접근하는 코드보다 훨씬 명료하다.

```python
for name, count in zip(names, letters):
    if count > max_letters:
        longest_name = name
        max_letters = count
```

훨씬 코드가 명료하고 깔끔하다.  

내장 함수 _zip_을 사용할 때의 문제점은 두 가지가 있다.

1. 파이썬 2에서 _zip_은 제너레이터가 아니다.
> 제공한 이터레이터를 완전히 순회해서 생성한 모든 튜플을 반환하기 때문에 
> 메모리를 많이 사용해서 프로그램이 망가질 수 있다.  
> 파이썬2 에서 매우 큰 이터레이터를 _zip_으로 묶어서 사용하려고 한다면 내장 모듈 _itertools_의 _izip_을 사용해야 한다.

2. 입력 이터러블들의 길이가 서로 다르다면 _zip_이 이상하게 동작한다.  
> 예를 들어 _names_ 리스트에만 다른 이름을 추가하고 _letters_는 그대로 둬서 두 리스트의 길이가 다르게 하자.

```python
names.append('Choi')

for name, count in zip(names, letters):
    print(name)

>>> Park
>>> Lee
>>> Kim
```
> 새 아이템 'Choi'가 없다.  
> _zip_은 이렇게 이터러블들의 길이가 다르면 가장 짧은 이터러블까지만 적용된다.  

그래서 만약 _zip_을 적용할 이터러블들의 길이가 같음을 확신할 수 없다면,  
내장 모듈 _itertools_의 *zip_longest*를 사용하는 방안도 생각할 수 있다.
<br><br>

### Part 2. 부록
_zip_을 재밌게 써볼 수도 있다.  

예를 들어 어떤 알고리즘 문제를 푸는데 원소의 다음 원소와 값을 비교해야 할 일이 있다고 해보자.

```python
from random import randint

k = [randint(1, 10) for _ in range(10)]
print(k)

# 바로 뒤 원소보다 큰 경우만 출력하자.

for i, n in enumerate(k[:-1]):
    if k[i] > k[i + 1]:
        print(k[i])

>>> [8, 9, 2, 9, 6, 9, 5, 10, 6, 1]
>>> 9
>>> 9
>>> 9
>>> 10
>>> 6
```
무난무난하고 평범한 계산이다.  
그런데 이 식을 _zip_을 사용해 재치 있게 사용해볼 수도 있다.

```python
from random import randint

k = [randint(1, 10) for _ in range(10)]
print(k)


for n1, n2 in zip(k[:-1], k[1:]):
    if n1 > n2:
        print(n1)

>>> [10, 9, 10, 7, 9, 7, 3, 5, 5, 5]
>>> 10
>>> 10
>>> 9
>>> 7
```
정말 어썸하지 않을 수 없다. 이런 활용도 있음을 참고하자.
<br>
<br>


### 핵심 정리

* 내장 함수 _zip_은 여러 이터러블을 병렬로 순회할 때 사용할 수 있다.
* 파이썬 3의 _zip_은 튜플을 생성하는 지연 제너레이터이다. 파이썬 2에서는 전체 결과를 튜플 리스트로 반환한다.
* 길이가 다른 이터레이터를 사용하면 _zip_은 그 결과를 조용히 잘라낸다.
* 내장 모듈 _itertools_의 *zip_longest*를 사용하면 이터레이터를 길이에 상관 없이 병렬로 순회할 수 있다.
