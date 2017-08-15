# Betteer way 30. 속성을 리팩토링하는 대신 @property를 고려하자


#### 139쪽
#### 2017/08/15 작성


## part 1. 구멍 난 양동이 예제 구현
내장 @property 데코레이터를 이용하면 더 간결한 방식으로 인스턴스 속성에 접근할 수 있다.  
고급 기법이지만 흔히 사용하는 @property 사용법 중 하나는 단순 숫자 속성을  
즉석에서 계산하는 방식으로 변경하는 것이다.  
호출하는 쪽을 변경하지 않고도 기존에 클래스를 사용한 곳이 새로운 동작을 하게 해주므로 유용하다.  
또한 시간이 지나면서 인터페이스를 개선할 때 중요한 임시방편이 된다.  
아마 이해가 안 갔을 것인데 예를 보자.  

이번 챕터에서는 구멍 난 양동이(leaky bucket) 알고리즘을 예로 든다.  
구멍 난 양동이 알고리즘은 네트워크에서 많이 사용하는 알고리즘으로,  
구멍이 나 꾸준히 양이 감소하는 양동이에 인풋을 넣어 넘치지 않게 관리하는 알고리즘이다.  
양동이가 넘치지 않게 하려면

1. 감소하는 양보다 적게 넣어야 하고, 
2. 한 번에 인풋을 넣을 때 양동이의 최대 부피를 넘지 않도록 해야 할 것이다.

여기서는 자세히 파고들기 보다는 구현 자체가 의미를 두었다.  
나도 몰라서 찾아봤기 때문에 설명했다. 이제 예시를 보도록 한다.

<br>
```python

from datetime import timedelta
from datetime import datetime

class Bucket:
    def __init__(self, period):
         self.period_delta = timedelta(seconds=period)
	 # 한 번 채우면 사용할 수 있는 시간(다 빠져나가기 까지)
	 self.reset_time = datetime.now()
	 # 양동이를 채운 최근 시간을 기록하는 변수
         self.quota = 0
	 # 투입물의 양을 기록하는 변수

	 def __repr__(self):
	     return "Bucket(quota={})".format(self.quota)
```

구멍 난 양동이 알고리즘은 양동이를 채울 때마다 투입물이  
다음 기간으로 넘어가지 않게 하는 식으로 동작한다.

<br>
```python

def fill(bucket, amount):
    now = datetime.now()
    if now - bucket.reset_time > bucket.period_delta:  # 시간이 지나 투입물이 모두 소진됐다면
        bucket.quota = 0
        bucket.reset_time = now
    bucket.quota += amount
```
또한 투입물을 소비하는 쪽에서는 매번 사용할 양을 뺄 수 있는지 확인해야 한다.

<br>
```python
def deduct(bucket, amount):
    now = datetime.now()
    if now - bucket.reset_time > bucket.period_delta:
        return False
    bucket.quota -= amount  # amount만큼 사용함
    return True
```


<br><br>
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

print('-' * 20 + '\n')

# 1만 남은 상태에서 더 소비하기
if deduct(bucket, 3):
    print("Had 3 quota")
else:
    print("Not enough for 3 quota")
    print(bucket)


>>>
Bucket(quota=100)
Had 99 quota
Bucket(quota=1)

--------------------
Not enough for 3 quota
Bucket(quota=1)
```

위 코드를 해석하자면 한 번 투입하면 다 소진하기까지 60초의 시간이 걸리는  
양동이를 생성하고 100만큼 투입한 뒤 99만큼 소진하고 3만큼 더 소진하는 코드이다.  
당연히 3만큼은 더 쓸 수 없고 3은 뺄 수 없다는 출력이 나왔다.  
<hr>
<br><br><br>

## part 2. @property와 @object.setter를 사용해 개선하기
위 구현은 잘 작동은 하지만 아름답지는 못하다.  
그 이유는 양동이의 투입물이 어느 수준에서 시작하는지 모른다는 것이다.  
양동이는 투입물이 0이 될 때까지 진행 기간 동안 할당량이 줄어든다.  
0이 되면 deduct가 항상 False를 반환한다. 이 때 deduct를 호출하는 쪽이  
중단된 이유가 Bucket의 할당량이 소진되어서인지, 아니면  
처음부터 Bucket에 할당량이 없어서인지 알 수 있으면 좋을 것이다.  
다시 말해 사용자 인터페이스가 아쉬운 상황.  

문제를 해결하기 위해 클래스에서 기간 동안 발생한 max_quota와 quota_consumed의 변경을 추적하도록 수정한다.  
또한 맨 처음에 언급한대로, **실행코드를 수정하지 않고** 실행가능하도록 할 것이다.  


```python
class Bucket:
    def __init__(self, period):
        self.period_delta = timedelta(seconds=period)
	self.reset_time = datetime.now()
	self.max_quota = 0
	self.quota_consumed = 0
				            
    def __repr__(self):
	return "Bucket(max_quota={}, quota_consumed={})".format(self.max_quota, self.quota_consumed)

							  
    # 밑 두 함수들은 직접 사용되는 것이 아닌 앞서 작성한 
    # fill과 deduct에서 사용되고 있다.
    # 그래서 앞서 쓴 사용코드를 수정하지 않아도 가능한 것
    @property
    def quota(self):
        return self.max_quota - self.quota_consumed
									        
    @quota.setter
    def quota(self, amount):
        delta = self.max_quota - amount
        if amount == 0:
            # 새 기간의 할당량을 리셋함
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

투입물의 양과 소비한 양을 추적하지 위한 변수 max_quota와 quota_consumed 변수를 추가했다.  

그리고 투입물의 양(quota)를 추적하는 프로퍼티와 세터도 같이 작성한다.  
이렇게 작성함으로써 원래 사용코드를 변경하지 않으면서 quota를 추적 가능하게 되었다.  
<br>

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

   
>>>
Initial Bucket(max_quota=0, quota_consumed=0)
Filled Bucket(max_quota=100, quota_consumed=0)
Had 99 quota
Now Bucket(max_quota=100, quota_consumed=99)
Had 3 quota
Still Bucket(max_quota=100, quota_consumed=201) 
```

위와 같이 작성함으로써 Bucket.quota를 사용하는 코드는 변경하거나  
Bucket 클래스가 변경된 사실을 몰라도 된다는 점이다. Bucket의 새 용법은  
잘 동작하며 max_quota와 quota_consumed에 직접 접근할 수 있다.  
<br><br>


#### 핵심정리
* 기존의 인스턴스 속성에 새 기능을 부여하려면 @property를 사용하자
* @property를 사용하여 점점 나은 데이터 모델로 발전시키자
* @property를 너무 많이 사용한다면 클래스와 이를 호출하는 모든 곳을 리팩토링하는 방안을 고려하자.
