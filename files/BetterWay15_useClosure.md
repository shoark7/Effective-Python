## Better way 15. 클로저가 변수 스코프와 상호 작용하는 방법을  알자.

#### 57쪽.
#### 2017/02/03 작성

### Part 1. 까다로운 Closure & Scope
숫자 리스트를 정렬할 때 특정 그룹의 숫자들이 먼저 오도록 우선순위를 매기려고 한다.  
이런 패턴은 사용자 인터페이스를 표현하거나, 다른 것보다 중요한 메시지나 예외 이벤트를 먼저 보여줘야 할 때 유용하다.  

이렇게 만드는 일반적인 방법을 리스트이 _sort_ 메서드에 헬퍼 함수를 _key_ 인수로 넘기는 것이다.  

헬퍼의 반환 값은 리스트에 있는 각 아이템을 정렬하는 값으로 사용된다.  
헬퍼는 주어진 아이템이 중요한 그룹에 있는지 확인하고 그에 따라 정렬키를 다르게 할 수 있다.

```python
def sort_priority(values, group):
    def helper(x):
        if x in group:					# 1. 클로저
            return (0, x)				# 2. 튜플 비교 규칙
        return (1, x)
    values.sort(key=helper)		        # 3. 일급 객체
    
numbers = [8, 3, 1, 2, 5, 4, 7, 6]
group = {2, 3, 5, 7}
sort_priority(numbers, group)
print(numbers)

>>> [2, 3, 5, 7, 1, 4, 6, 8]
```

개인적으로 이 함수는 너무 어썸해서 모두에게 공유했으면 하는 코드다.  
_group_에 속하는 숫자들이 우선적으로 정렬되었다. 이 코드가 동작하는 이유는 크게 세 가지가 있다.

1. 파이썬은 클로저를 지원한다.  
> **클로저(closure)란 자신이 정의된 스코프에 있는 변수를 참조하는 함수다.**  
>바로 이 점 때문에 _helper_ 함수가 *sort_priority* 스코프에 있는 _group_인수에 접근할 수 있다.  

2. 함수는 파이썬에서 **일급 객체**(first-class object)이다.
> 함수를 직접 참조하고, 변수에 할당하고, 다른 함수의 인수로 전달하고, 표현식과 if 문 등에서 비교할 수 있다.  
> 파이썬에서는 당연하다고 생각했는데 되지 않는 언어도 있다는 뜻.  
> **따라서 _sort_ 메서드에서 클로저 함수를 _key_ 인수로 받을 수 있었다.**  

3. 파이썬에는 이터러블을 비교하는 특정한 규칙이 있다.  
> 먼저 인덱스 0의 아이템을 비교하고 같다면 1의 아이템, ... 과 같이 비교한다.  
> **_sort_는 기본적으로 오름차순이다. 그래서 조건에 맞는 값을 0으로 보내서 1인 다른 값들보다 먼저 보이게 한 것!!**

<br><br>

함수에서 우선순위가 높은 아이템을 발견했는지 여부를 반환해서 사용자 인터페이스 코드가 그에 따라 동작하게 하면 좋을 것이다.  
이런 동작을 추가하는 일은 쉬워보인다.  

```python
def sort_priority2(numbers, group):
    found = False		# flag를 두고 값을 찾으면 True로 전환!!
    def helper(x):
        if x in group:
            found = True	# 찾으면 여기서!!
            return 0, x
        return 1, x
    numbers.sort(key=helper)
    return found
found = sort_priority2(numbers, group)
print('Found', found)

>>> False  # what the?
```

_numbers_나 _group_ 코드는 전혀 바뀌지 않았는데 _found_ 값이 True가 아니다.  
정상적으로 값을 찾아서 flag가 뒤집혔어야 하는데 말이다.  왜 이런 일이??  

구체적인 답안을 알기 전에 파이썬의 **scope**(범위)를 생각해봐야 한다.  
파이썬에서는 다양한 구역에서의 변수, 함수명들이 뒤섞여 namespace를 오염시키지 않게  
scope을 둬서 각 변수, 함수들이 영향을 미치는 공간을 한정하고 있다.  

예를 들어 내가 리스트의 최대값을 구하는 함수를 만들었고 그 최대값을 _max_라는 변수에 담았다고 치자.  
그런데 **이미 파이썬에는 _max_라는 내장 함수가 있고 내가 정한 _max_라는 이름과 정확히 겹친다.**  
값이 완전히 치환되면 차후 _max_라는 함수를 영영 쓸 수 없을 것이다.  

그것을 막기 위해 내가 만든 _max_변수는 함수 안에서, 함수 스코프 내에서만 의미가 있고,  
그 밖의 공간에서는 참조가 되지 않게 해놓았다.(실제로 해보자)  
이렇게 함으로써 전역 공간의 namespace가 오염되는 것을 막은 것이다.  
이렇게 **scope는 각 변수, 함수명들이 영향을 미치는 범위를 의미한다고 생각하면 좋다.**  

표현식에서 변수를 참조하면 파이썬 인터프리터는 참조를 해결하려고 다음과 같은 순서로 스코프를 탐색한다.  

1. 현재 함수의 스코프(위의 helper 함수)
2. (현재 스코프를 담고 있는 다른 함수 같은) 감싸고 있는 스코프(위의 sort_priority 함수)
3. 코드를 포함하고 있는 모듈의 스코프(전역 스코프라고도 함)
4. (len이나 str 같은 함수를 담고 있는) 내장 스코프

이 중 어느 스코프에도 참조한 이름으로 된 변수가 정의되어 있지 않으면 NameError 예외가 일어난다.  

첫 번째 예제 같은 경우에는 _group_이 2번 경우에 해당하여 _group_을 _helper_함수에서도 쓸 수 있었던 것이다.  

**그러면 두 번째 예제에서 _found_는 왜 문제가 되었던 것인가?**  

그 이유는 **참조할 때와 달리 변수에 값을 할당할 때는 다른 방식으로 동작하기 때문이다.**  

파이썬은 변수에 값을 할당할 때 변수가 현재 스코프에 존재하지 않으면 바깥 스코프와 관계 없이 새로운 변수 정의로 취급한다.  
새로 정의되는 변수의 스코프는 그 할당을 포함하고 있는 함수가 된다.  
코드를 다시 보자.


```python
def sort_priority2(numbers, group):
    found = False		# sort_priority2의 스코프
    def helper(x):
        if x in group:
            found = True	# helper의 스코프
            return 0, x
        return 1, x
    numbers.sort(key=helper)
    return found		# sort_priority2의 스코프
found = sort_priority2(numbers, group)
print('Found', found)
```
_helper_함수에서 _found_의 값에 True를 할당하고 있다.  
할당이기 때문에 현재 존재하지 않았던 _found_에는 True가 할당되었고 이는 바깥쪽 _found_와는 엄연히 다른 값이다.  
값을 참조한 것이 아닌 것이다.  

*sort_priority2* 함수는 마지막에 _found_를 리턴하는데 여기서 _found_는,  
_helper_의 스코프가 아닌 *sort_priority* 스코프의 값을 반환하기 때문에 True가 아닌 False를 반환하는 것이다.  
<br>


이 문제는 꽤 까다로워서 때로는 스코프 버그(scoping bug)라고도 한다.  
하지만 언어 설계자의 의도라고 한다.  
이 동작은 함수의 지역 변수가 자신을 포함하는 모듈을 오염시키는 문제를 막아준다.  
그렇지 않았다면 함수 안에서 일어나는 모든 할당이 전역 모듈 스코프에 쓰레기를 넣는 결과로 이어졌을 것이다.  
이로 인해 생기는 버그는 꽤 파악하기 어렵다.
<br><br><br>


### Part 2. 해결방안

#### 2.1. nonlocal로 데이터 얻어오기
파이썬 3에는 클로저에서 데이터를 얻어오는 특별한 문법이 있는데 _nonlocal_을 사용하는 것이다.  
이것은 **특정 변수 이름에 할당할 때 스코프 탐색이 일어나야 함을 나타낸다.**  
유일한 제약은 _nonlocal_이 전역 변수의 오염을 피하기 위해 모듈 수준 스코프까지는 탐색할 수 없다는 것이다.(2번까지만)  

사용 예시는 다음과 같다.

```python
def sort_priority3(numbers, group):
    found = False
    def helper(x):
        nonlocal found
        if x in group:
            found = True
            return 0, x
        return 1, x
    numbers.sort(key=helper)
    return found
```
`nonlocal found`이라는 문장을 통해 _found_ 변수에 값이 할당되면 이 스코프에 변수를 새로 만드는 것이 아니라,  
스코프 탐색을 통해 변수를 찾아서 값을 주라는 구문으로 변하였다.  

_nonlocal_ 문을 통해 클로저에서 데이터를 다른 스코프에 할당하는 시점을 알아보기 쉽게 해준다.  
_nonlocal_ 문은 변수 할당이 모듈 스코프에서 직접 들어가게 하는 _global_문을 보완한다.  

하지만 전역 변수의 안티패턴과 마찬가지로 간단한 함수 의외에는 _nonlocal_을 사용하지 않도록 주의해야 한다.  
_nonlocal_의 부작용은 특히 알아내기 어렵고,  
_nonlocal_ 문과 관련 변수에 대한 할당이 멀리 떨어진 긴 함수에서는 이해하기 더욱 어렵다.  

주의해서 쓰도록 하자.
<br><br>

#### 2.2. 헬퍼 클래스로 감싸자.
이건 일단 코드를 봐야 안다.

```python
class Sorter:
    def __init__(self, group):
        self.group = group
        self.found = False
        
    def __call__(self, x):
        if x in self.group:
            self.found = True
            return 0, x	# 튜플은 ( )로 안 감싸도 된다.
        return 1, x
    
sorter = Sorter(group)
numbers.sort(key=sorter)
assert sorter.found is True
```
여기서 _Sorter_는 헬퍼 클래스다.  
_sort_ 메서드의 _key_에 _Sorter_ 클래스 인스턴스를 넣고 있는데  
클래스를 호출할 수 있기 위해서는(callable 하게 만들기 위해서는) \__call__ 메서드를 정의해야 한다.  
call 되는 순간 _x_ 라는 값을 _self.group_에 있는지 검정하여 계산한다.  
결과는 똑같다.
<br><br>


#### 핵심 정리
* 클로저 함수는 자기 자신이 정의된 스코프 중 어디에 있는 변수도 참조할 수 있다.
* 기본적으로 클로저에서 변수를 할당하면 바깥쪽 스코프에는 영향을 미치지 않는다.
* 파이썬 3에서는 _nonlocal_ 문을 사용하여 클로저를 감싸고 있는 스코프의 변수를 수정할 수 있다.
