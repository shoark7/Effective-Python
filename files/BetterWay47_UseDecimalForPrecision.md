## Better Way 47. 정밀도가 중요할 때는 decimal을 사용하자

#### 243쪽

* Created : 2019/06/29
* Modified: 2019/06/29

<br>

## 1. 부동 소수점 연산의 문제점

파이썬은 숫자 데이터를 다루는 코드를 작성하기에 아주 뛰어난 언어다. 파이썬의 정수 타입은 현실적인 크기의 값을 모두 표현할 수 있다. 다른 언어처럼, 32 비트, 64비트에 얽매이지 않는다. 배정밀도 부동 소수점 타입은 IEEE 754 표준을 따른다. 심지어 파이썬 언어는 허수 값을 표현하는 타입도 갖고 있다. 그러나 이것만으로 모든 상황을 충족시키지는 못한다.  

예를 들어, 고객에게 부과할 국제 전화 요금을 계산한다고 하자. 고객이 몇 분, 몇 초간 통화했는지 알고 있다. 또한 서울에서 울릉도를 건너 통화했을 때의 요율 등도 정해져 있따. 그렇다면 요금을 얼마나 지불해야 할까?

부동 소수점 연산을 통한 계산은 일견으로는 합리적으로 보인다.


```python
rate = 1.45
seconds = 10 * 60 + 42
cost = rate * seconds / 60

print(cost)

15.514999999999999
```

부동 소수점의 전형적인 문제가 드러났다. **바로 소수점간 연산시 소수값이 지리멸렬하게 남는다는 것.** 뭐 그래도 괜찮다. 우리는 소수점을 반올림하는 `round`라는 내장 함수를 가지고 있으니까.


```python
print(round(cost, 2))

15.51
```

<br>

이에 더해 연결 비용이 훨씬 저렴한 곳 사이에서 일어나는 아주 짧은 통화도 지원해야 한다고 하자. 다음은 분당 0.5원 요율로 5초 동안 일어난 통화의 요금을 계산한 것이다.

```python
rate = 0.05
seconds = 5
cost = rate * seconds / 60

print(cost)

0.004166666666666667
```

부동 소수점의 결과가 너무 작아서 반올림하면 0이 된다. 이렇게 계산하면 안 된다.

```python
print(round(cost, 2))

0.0
```

확실히 뭔가 해결책이 필요하다.

<br>

## 2. 해결책: Decimal 사용하기

해결책은 **내장 모듈 [decimal](https://docs.python.org/3/library/decimal.html)의 Decimal 클래스를 사용하는 것이다. Decimal 클래스는 기본적으로 소수점이 28자리인 고정 소수점 연산을 제공하며 필요하다면 더 늘릴 수도 있다.** Decimal을 사용하면 IEEE 754 부동 소수점 수의 정확도 문제를 피해갈 수 있다. 또한 반올림 연산을 더 세밀하게 제어할 수도 있다.

앞선 예제의 울릉도 문제를 Decimal로 다시 계산해보자.


```python
from decimal import Decimal 

rate = Decimal('1.45')
seconds = Decimal(str(10 * 60 + 42))
cost = rate * seconds / Decimal('60')
print(cost)

15.515
```

아까와 달리 정확한 값이 나온다.  

Decimal 클래스에는 원하는 반올림 동작에 따라 필요한 소수점 위치로 정확하게 반올림하는 내장 함수가 있다.

```python
from decimal import ROUND_UP

rounded = cost.quantize(Decimal('0.01'), rounding=ROUND_UP)
print(rounded)

15.52
```

이 방식으로 quantize 메소드를 사용하면 짧고 저렴한 통화에 해당하는 적은 통화료도 적절하게 처리할 수 있다. 다음 예에서 통화 요금을 Decimal로 나타낸 비용이 여전히 0.01원 이하임을 알 수 있다.

```python
rate = Decimal('0.05')
seconds = Decimal('5')
cost = rate * seconds / Decimal('60')
print(cost)

0.004166666666666666666666666667
```

하지만 다음과 같이 정량화(quantize)하면 1원으로 반올림된다.

```python
rounded = cost.quantize(Decimal('0.01'), rounding=ROUND_UP)
print(rounded)

0.01
```
 
Decimal이 고정 소수점 수에도 잘 동작하지만 아직도 정확도 면에서는 제약이 있다. 예를 들어 1/3은 근사값으로 표현되는 것 등이 그렇다. 정확도에 제한이 없는 유리수를 표현하려면 내장 모듈 fractions의 Fraction 클래스를 사용해야 한다.

<br>

## 3. 핵심 정리

* 파이썬은 현실적으로 모든 유형의 숫자 값을 표현할 수 있는 내장 타입과 클래스를 모듈로 제공한다.
* Decimal 클래스는 화폐 연산처럼 정밀도가 높고 정확한 반올림이 필요한 상황에 안성맞춤이다.
