## Better Way 30. 속성을 리팩토링하는 대신 @property를 고려하자

#### 139쪽

* Created : 2017/08/15
* Modified: 2019/06/03 


<br>

## 1. 구멍 난 양동이 예제 구현

[29장](https://github.com/shoark7/Effective-Python/blob/master/files/BetterWay29_dontusegetter.md)에서 확인한 바와 같이 **내장 @property 데코레이터를 이용하면 더 간결한 방식으로 인스턴스 속성에 접근할 수 있다.** 고급 기법이지만 흔히 사용하는 @property 사용법 중 하나는 **단순 숫자 속성을 개별 변수를 두는 대신 즉석에서 계산하는 방식으로 변경하는 것이다. 이는 최근 실제 프로젝트에서 사용했던 기법인데 이렇게 하면 호출하는 쪽을 변경하지 않고도 기존에 클래스를 사용한 곳이 새로운 동작을 하게 해주므로 유용하다.** 또한 시간이 지나면서 인터페이스를 개선할 때 중요한 임시방편이 된다.  

이에 대한 예로 **구멍 난 양동이(leaky bucket) 알고리즘**을 짜보자. 이 예제는 눈으로 따라갈 때는 한 번에 이해가 안 갔다. 헷갈리면 '콩쥐와 팥쥐'에서 콩쥐가 구멍 난 항아리에 물을 퍼채우는 일화를 생각하자. 물을 꾸준히 채울 수 있지만(fill), 시간이 지남에 따라 자연스럽게 액체가 유실된다.(leak) 구멍이 나 꾸준히 양이 감소하는 양동이에 인풋을 넣어 넘치지 않게 관리하려면

1. **감소하는 양보다 적게 넣어야 하고,**
1. **한 번에 인풋을 넣을 때 양동이의 최대 부피를 넘지 않도록 해야 할 것이다.**

여기서는 자세히 파고들기보다는 구현 자체가 의미를 두었다. 나도 몰라서 찾아봤기 때문에 설명했다.

먼저 **확장 등을 고려하지 않은 채 초기 수요를 느끼고 구멍 난 양동이의 할당량을 일반 파이썬 객체로 구현하려 한다고 하자.** 다음 Bucket 클래스는 남은 할당량과 이 할당량을 이용할 수 있는 기간을 표현한다.


```python
from datetime import datetime, timedelta

class Bucket:
    def __init__(self, period):
        self.period_delta = timedelta(seconds=period)
        # 한 번 채우면 사용할 수 있는 시간(다 새기까지)
        self.reset_time = datetime.now()
        # 양동이를 채운 최근 시간을 기록
        self.quota = 0
        # 투입물의 양을 기록(quota: 할당량)

    def __repr__(self):
        return "Bucket(quota={})".format(self.quota)
```


이 양동이 객체를 사용하는 함수를 두 개 만들어보자. **하나는 양동이에 새로 물을 퍼넣는 _fill_ 함수, 다른 하나는 퍼내는 _deduct_ 함수다.**

먼저 _fill_ 함수는 시간이 오래 지나 물이 모두 샜다면 양동이의 양을 0으로 재설정하는 로직을 구현한다.

```python
def fill(bucket, amount):
    now = datetime.now()
    # 내용물이 모두 빠져나갈 만큼 시간이 오래됐으면,
    # 물이 다 빠져나갔을 것이기 때문에 quota를 0으로 두고, 시간 리셋
    if now - bucket.reset_time > bucket.period_delta:
        bucket.quota = 0
        bucket.reset_time = now
    bucket.quota += amount
```


또한 소비하는 _deduct_ 함수에서는 매번 사용할 양을 뺄 수 있는지 확인해야 한다.


```python
def deduct(bucket, amount):
    now = datetime.now()

    # 시간이 너무 지나 물이 다 떨어짐. 퍼낼 수 없다.
    if now - bucket.reset_time > bucket.period_delta:
        return False
    # 퍼낼 양이 지금 양동이의 물 양보다 많다.
    elif bucket.quota < amount:
        return False

    bucket.quota -= amount  # amount만큼 물을 퍼냄
    return True
```

<br>


이 클래스를 사용하기 위해 양동이를 채우고 필요한 만큼 빼보자.

```python
bucket = Bucket(60)
fill(bucket, 100)
print(bucket)

if deduct(bucket, 99):
    print("Had 99 quota")
else:
    print("Now enough for 99 quota")
    print(bucket)


Bucket(quota=100)
Had 99 quota
```

_fill_ 을 통해 양동이에 100만큼 채워놓고 _deduct_ 를 통해 99만큼을 퍼냈다.

```python
# 1만 남은 상태에서 더 소비하기
if deduct(bucket, 3):
    print("Had 3 quota")
else:
    print("Not enough for 3 quota")
    print(bucket)


Not enough for 3 quota
Bucket(quota=1)
```

작업 후 물이 1만 남은 상태에서 3을 추가로 퍼내는 작업은 실행되지 않는다. 상식적으로 가진 것보다 더 내놓을 수는 없으니까.

여기까지는 문제가 없다. 만약 프로그램의 요구사항이 여기서 멈추고 프로젝트가 중지된다면 이 정도도 나쁘지 않을 수 있다.

<br>


## 2. @property와 setter를 사용해 리팩토링하기

위 구현은 잘 작동은 하지만 아름답지는 못하다. 그 이유는 **양동이의 투입물이 어느 수준에서 시작하는지 모른다는 것이다.**  
양동이는 투입물이 0이 될 때까지 진행 기간 동안 할당량이 줄어든다. 0이 되면 _deduct_ 가 항상 False를 반환한다. 이때 **_deduct_ 를 호출하는 쪽 입장에서 중단된 이유가 Bucket의 할당량이 소진되어서인지, 아니면 처음부터 Bucket에 할당량이 없어서인지 알 수 있으면 좋을 것이다.**

다시 말해 사용자 인터페이스가 아쉬운 상황.  

문제를 해결하기 위해 클래스에서 기간 동안 발생한 _max\_quota_ 와 _quota\_consumed_ 의 변경을 추적하도록 수정한다.  

또한 맨 처음에 언급한대로, **맨 처음(1장) 짠 실행코드는 수정하지 않고, 리팩토링 이후에도 문제없이 실행가능하도록 할 것이다.** 이것이 정말정말 중요하다.

<br>

Bucket 클래스를 앞서 언급한 두 변수를 사용해 개선하자. 이제는 **_quota_ 변수는 @property를 사용해 동적으로 현재 할당량의 수준을 계산하도록 할 것이다.**

```python
class Bucket:
    def __init__(self, period):
        self.period_delta = timedelta(seconds=period)
        self.reset_time = datetime.now()
        self.max_quota = 0
        self.quota_consumed = 0

    def __repr__(self):
        return "Bucket(max_quota={}, quota_consumed={})".format(self.max_quota, self.quota_consumed)


    # quota를 동적으로 계산해 확인한다.
    @property
    def quota(self):
        return self.max_quota - self.quota_consumed

    # quota에 동적으로 변화를 준다.
    @quota.setter
    def quota(self, amount):
        delta = self.max_quota - amount
        if amount == 0:
            # quota를 0으로 할당하는 것은 새 기간의 할당량을 리셋하는 것
            self.quota_consumed = 0
            self.max_quota = 0
        elif delta < 0:
            # 새 기간의 할당량을 채움
            assert self.quota_consumed == 0
            self.max_quota = amount
        else:
            # 기간 동안 할당량을 소비함.
            assert self.max_quota >= self.quota_consumed
            self.quota_consumed += delta
```

투입물의 양과 소비한 양을 추적하기 위한 변수 _max\_quota_ 와 _quota\_consumed_ 변수를 추가했다.  

그리고 **투입물의 양(quota)를 동적으로 추적하는 @property와 setter 메소드도 같이 작성한다.** 이렇게 작성함으로써 원래 사용코드를 변경하지 않으면서 quota를 추적 가능하게 되었다.  

```python
bucket = Bucket(60)
print("Initial", bucket)
fill(bucket, 100)
print("Filled", bucket)

if deduct(bucket, 99):
    print("Had 99 quota")
else:
    print("Not enough for 99 quota")

print("Now", bucket)
   
if deduct(bucket, 3):
    print("Had 3 quota")
else:
    print("Not enough for 3 quota")
        
print("Still", bucket)

   
Initial Bucket(max_quota=0, quota_consumed=0)
Filled Bucket(max_quota=100, quota_consumed=0)
Had 99 quota
Now Bucket(max_quota=100, quota_consumed=99)
Not enough for 3 quota
Still Bucket(max_quota=100, quota_consumed=99)
```

몇 번을 강조하지만 **@property와 setter를 사용해서 속성을 리팩토링한 장점은 사용자 입장에서 처음에 작성한 bucket.quota를 사용한 코드를 변경하거나, Bucket 클래스가 변경된 사실을 몰라도 된다는 점이다.** Bucket의 새 용법은 잘 동작하며 _max\_quota_ 와 _quota\_consumed_ 에 직접 접근할 수 있다.  


<br>

## 3. 핵심 정리

* 기존의 인스턴스 속성에 새 기능을 부여하려면 @property를 사용하자
* @property를 사용하여 점점 나은 데이터 모델로 발전시키자
* 그렇다고 과용하지 말자. @property를 너무 많이 사용한다면 클래스와 이를 호출하는 모든 곳을 리팩토링하는 방안을 고려하자.
