# Better way 05. 시퀀스를 슬라이스하는 방법을 알자.

#### 28쪽

* Created : 2016/12/25
* Modified: 2019/05/03  


## 1. Slice tricks

**파이썬은 다른 프로그래밍 언어와 마찬가지로 리스트 등의 시퀀스를 슬라이스해서 조각으로 만드는 문법을 제공한다. 이를 통해 시퀀스의 부분집합을 쉽게 구할 수 있다.**

간단한 시퀀스의 예로는 list, str, bytes가 있을 것이다. 추가로 \_\_getitem\_\_과 \_\_setitem\_\_이라는 특별한 메소드를 구현하는 다른 파이썬의 클래스에도 슬라이싱을 적용할 수 있다.  

슬라이스의 기본 형태는 somelist[start:end]이다. 다른 언어와 같이 start는 포함되고 end는 제외된다.([start, end))

```python
a = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',]

print('First four', a[:4])      # 1.
print('Last four', a[:-4])      # 2.
print('Middle two', a[3:-3])    # 3.


['a', 'b', 'c', 'd']
['e', 'f', 'g', 'h']
['d', 'e'] 
```

1. 첫 원소 4개를 추출한다. 리스트의 처음부터 슬라이스할 때는 보기 편하게 인덱스 0을 생략한다. 리스트의 끝까지 슬라이스 할 때도 마지막 인덱스는 넣지 않아도 된다.
2. 마지막 원소 4개를 추출한다. 리스트의 끝을 기준으로 계산할 때는 음수로 슬라이스하는 게 편하다.
3. 3번째 원소에서 끝에서 3번째 원소까지 추출한다.


```python
a[:]        # ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
a[:5]       # ['a', 'b', 'c', 'd', 'e']
a[:-1]      # ['a', 'b', 'c', 'd', 'e', 'f', 'g']
a[4:]       #                     ['e', 'f', 'g', 'h']
a[-3:]      #                          ['f', 'g', 'h']
a[2:5]      #           ['c', 'd', 'e']
a[2:-1]     #           ['c', 'd', 'e', 'f', 'g']
a[-3:-1]    #                          ['f', 'g']

```

**슬라이싱은 start와 end 인덱스가 리스트의 경계를 벗어나도 적절하게 처리한다.**(에러가 봔환되지 않고 대신 빈값이 나온다.)  
덕분에 입력 시퀀스에 대응해 처리할 최대 길이를 코드로 쉽게 설정할 수 있다.

```python
first_twenty = a[20:]
last_twenty = a[:20]

print(first_twenty)
print(last_twenty)

[]
['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
```

start와 end가 배열의 크기를 훨씬 추월했지만 에러가 발생하지 않았다. 하지만 **Sequence의 길이를 넘어서는 인덱스를 직접 접근하면 에러가 발생한다.**

```python
a[20]  # Error!!
```


**슬라이싱의 결과는 완전히 새로운 리스트이다.** 원본 리스트에 들어 있는 객체에 대한 참조는 유지되지만, 슬라이스 결과를 수정해도 원본에는 영향을 미치지 않는다.


```python

b = a[:4]
print('Before:   ', b)  # ['e', 'f', 'g', 'h']
b[1] = 99
print('After :   ', b)  # ['e', 99 , 'g', 'h']
print('No Change:', a)  # ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
```

_a_ 를 슬라이스한 _b_ 에 변화를 가해도 _a_ 는 변하지 않았다.


<br>

슬라이스를 할당에 사용하면(좌변에 두면) 원본 리스트에서 지정한 범위를 대체한다. 슬라이스 할당의 길이는 달라도 되며, 할당받은 슬라이스의 앞뒤 값은 유지된다.  리스트는 새로 들어온 값에 맞춰 늘어나거나 줄어든다.

```python
print('Before : ', a)  # ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
a[2:7] = [99, 24, 14]
print('After  : ', a)  # ['a', 'b', 99, 22, 14, 'h']
```

<br>

**시작과 끝 인덱스를 모두 생략하고 슬라이스하면 원본의 복사본을 얻는다.**

```python
b = a[:]
assert b == a and b is not a
# b와 a가 내용이 같지만 서로 다른 객체임을 확인하는 assert문이다.
```

슬라이스에 시작과 끝 인덱스를 지정하지 않고 할당하면(새 리스트를 할당하지 않고) 슬라이스의 전체 내용을 참조 대상의 복사본으로 대체한다.

```python
b = a
print('Before', a)  # ['a', 'b', 99, 22, 14, 'h']
a[:] = [101, 102, 103]
assert a is b
print('After ', a)  # [101, 102, 103]
```


만약 _a[:]_ 가 아닌 _a = [101, 102, 103]_ 이렇게 했다면,
_a_ 가 가리키는 리스트 객체가 바뀌어 _a_ 와 _b_ 는 달라질 것이다.

반대로 _a[:]_ 를 할당에 사용하면 객체의 참조가 아닌, 객체 자체의 값이 변한다.

<br>

## 2. 핵심 정리

* 너무 장황하게 하지 말자. start에 0을 쓰거나 end에 시퀀스의 길이를 설정하지 말자.
* 슬라이싱은 범위를 벗어난 인덱스를 허용하므로, a[:1000000]와 같은 것도 에러가 나지 않는다.
* list 슬라이스에 할당하면(왼쪽에 두면) 원본 시퀀스의 지정한 범위를 대체한다.