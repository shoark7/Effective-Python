# Better way 06. 한 슬라이스에 start, end, stride를 함께 쓰지 말자

#### 32쪽

* Created : 2017/01/10
* Modified: 2019/05/04  


## 1. stride의 기본을 알자

파이썬은 기본 슬라이싱뿐만 아니라 _somelist[start\:end\:stride]_ 처럼 슬라이싱의 간격(stride)를 지정하는 특별한 문법도 있다.

이 문법을 사용하면 **시퀀스(Sequence)를 슬라이스할 때 매 n번째 아이템을 가져올 수 있다.** 예를 들어 stride를 쓰면 리스트에서 홀수와 짝수 인덱스를 손쉽게 그룹으로 묶을 수 있다.


```python

a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = a[::2]
odds = a[1::2]

# 값이 아니라 인덱스다!
print("Evens are ", evens)  # Even indices are  [1, 3, 5, 7, 9]
print("Odds are", odds) # Odd indeices are [2, 4, 6, 8, 10]
```

문제는 stride 문법이 종종 예상치 못한 동작을 해서 버그를 만들어내기도 한다는 것이다.   
예를 들어 파이썬에서 바이트 문자열을 역순으로 만드는 일반적인 방법은 스트라이트 -1로 문자열을 슬라이스하는 것이다.

```python
x = b'mongoose'
y = x[::-1]
print(y)  # b'esoognom'
```


위의 코드는 바이트 문자열이나 아스키 문자에는 잘 동작하지만, UTF-8 바이트 문자열로 인코드된 유니코드 문자에는 원하는 대로 동작하지 않는다.

```python
w = '김철수'
x = w.encode('utf-8')
y = x[::-1]

z = y.decode('utf-8')
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x98 in position 0: invalid start byte.
```

이 이슈는 주요 인코딩 방식인 UTF-8에 종속되는 문제로, 인코딩에 대한 이해가 부족하면 쉽게 이해할 수 없는 문제이기도 하다.


<br>

## 2. stride의 주요 문제점

```python
a = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
print(a[::2])   # ['a', 'c', 'e', 'g']
print(a[::-2])  # ['h', 'f', 'd', 'b']
```

`::2`는 처음부터 시작해서 매 두 번째 아이템을 선택하라는 의미이다.  
`::-2`는 끝부터 시작해서 반대 반향으로 매 두 번째 아이템을 선택하라는 의미이다.  

이건 뭘까?

```python
print(a[2::2])     # ['c', 'e', 'g']
print(a[-2::-2])   # ['g', 'e', 'c', 'a']
print(a[-2:2:-2])  # ['g', 'e']
print(a[2:2:-2])   # []
```

물론 고민하면 이해할 수는 있다. 문제는 슬라이싱의 stride 문법이 매우 혼란스러울 수 있다는 것이다. 대괄호 안에 숫자가 세 개나 있으면 빽빽해서 읽기 힘들다.  

그래서 start, end 인덱스가 stride와 연계되어 어떤 작용을 하는지 분명하지 않다.
특히 stride가 음수이면 더더욱 그렇다.

이런 문제를 방지하려면 가급적 **start, end, stride를 함께 사용하지 말아야 한다.**

<br>

Sequence를 slicing할 때, stride를 쓰고 싶다면 다음을 기억하도록 하자.

* **stride를 사용해야 하면 양수 값을 사용하고, start, end를 생략하자.**
* **stride를 start나 end와 함께 꼭 사용해야 한다면**
    1. **stride를 적용한 결과를 변수에 할당하고**
    2. **이 변수를 슬라이스한 결과를 다른 변수에 할당해서 사용하자.**


```python
b = a[::2]   # ['a', 'c', 'e', 'g']
c = b[1:-1]  # ['c', 'e']
```

슬라이싱부터 하고 스트라이딩을 하면 데이터의 얕은 복사본(shallow copy)가 추가로 생긴다. 첫 번째 연산은 결과로 나오는 슬라이스의 크기를 최대한 줄여야 한다.

프로그램에서 두 과정에 필요한 시간과 메모리가 충분하지 않다면 내장 모듈 _itertools_ 의 _islice_ 메서드를 사용해보자.

<br>


## 3. 핵심정리

* 한 슬라이스에 start, end, stride를 같이 지정하면 매우 혼란스러울 수 있다.
* 슬라이스에 start와 end 인덱스 없이 양수 stride 값을 사용하자. 음수 stride 값은 가능하면 피하자.
* 한 슬라이스에 start, end, stride를 함께 사용하는 상황은 피하자. 꼭 필요하면 두 번 할당하거나, 내장 모듈 _itertools_ 의 _islice_ 를 사용하자.
