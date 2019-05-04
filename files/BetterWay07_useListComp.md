# Better way 07. _map_ 과 _filter_ 대신에 리스트 컴프리헨션을 사용하자

#### 34쪽

* Created : 201?/??/??
* Modified: 2019/05/04  


<br>

## 1.

파이썬에는 하나의 iterable에서 리스트를 만들어내는 간결한 문법이 있다. 이를 리스트 컴프리헨션(list comprehension)이라고 한다.

예를 들어 _list_ 에 있는 각 수의 제곱을 게산한다고 하자. 리스트 컴프리헨션을 쓰면 리스트와, 관련된 _range_ 등의 객체에 할당과 연산을 한 번에 같이 할 수 있다.


```python
a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
r = range(1, 11)

assert [i ** 2 for i in a] == [j ** 2 for j in r]
```

똑같은 식을 내부 함수인 map을 통해서도 할 수 있지만 복잡해보인다.

```python
map_one = map(lambda x: x ** 2, a)
```

<br>

## 2.


또한 리스트 컴프리헨션은 map과 달리 리스트에 있는 아이템을 편하게 걸러낼 수도 있다. 예를 들어 제곱수가 짝수인 수만 걸러내서 제곱수를 구한다고 해보자.

```python
even_squares = [i ** 2 for i in range(1, 11) if i % 2 == 0]

# 내장 함수 filter와 map을 사용하면 같은 결과를 얻지만 복잡해 보인다.
map_squares = map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, a))

assert even_squares == list(map_squares)
```

<br>

## 3. Comprehension expression의 다른 사용처

dict와 set에도 리스트 컴프리헨션에 해당하는 문법이 있다.

```python
chile_ranks = {'ghost': 1, 'habanero': 2, 'cayene': 3}
ranks_dict = {value: key for key, value in chile_ranks.items()}

print(ranks_dict) # {1: 'ghost', 2: 'habanero', 3: 'cayene'}


chile_len_set = {len(name) for name in ranks_dict.values()}
print(chile_len_set) # {8, 5, 6}
```

<br>

## 4. 핵심정리

* 리스트 컴프리헨션은 추가적인 lambda 표현식이 필요 없어서, 내장 함수인 _map_, _filter_ 를 사용하는 것보다 명확하다.
* 리스트 컴프리헨션을 사용하면 입력 리스트에서 아이템을 간단히 건너뛸 수 있다. _map_ , _filter_ 로는 그렇지 않다.
* _dict_ 와 _set_ 도 컴프리헨션 표현식을 지원한다.
