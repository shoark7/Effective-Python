## Better Way 45. 지역 시간은 time이 아닌 datetime으로 표현하자

#### 231쪽

* Created : 2019/06/24
* Modified: 2019/06/24

<br>

## 1. time과 datetime 모듈

협정 세계시(UTC, Coordinated Universal Time)는 시간대에 의존하지 않는 표준 시간 표현이다. UTC는 유닉스 기원 이후로 지나간 초로 시간을 표현하는 컴퓨터에서 잘 작동한다. 하지만 이런 단순 '초'는 사람에게는 잘 안 맞는다.  

사람이 사용하는 시간은 현재 자신이 있는 위치를 기준으로 한다. 사람들은 'UTC 15:00 - 7시'가 아니라 '정오' 혹은 '아침 8'시라고 말한다. **프로그램에서 시간을 처리해야 한다면 사람이 이해하기 쉽게 UTC와 지역 시간 사이에서 변환해야 한다.**  

파이썬은 두 가지 시간대 변경 변환 방법을 제공한다. 내장 모듈 time을 사용하는 이전 방법은 치명적인 오류가 일어날 가능성이 크다. 내장 모듈 datetime을 사용하는 새로운 방법은 커뮤니티에서 많든 `pytz` 패키지의 도움을 받아 훌륭하게 동작한다.

datetime이 최선의 선택이고, time을 사용하지 말아야 하는 이유를 완전히 이해하는 것이 이번 장의 내용이다.


<br>

## 2. time 모듈 사용하기

내장 모듈 time의 localtime 함수는 유닉스 타임스탬프(UTC에서 유닉스 기원, epoch 이후 지난 초)를 호스트 컴퓨터의 시간대(나는 Asia/Seoul)와 일치하는 지역 시간으로 변환한다.

```python
from time import localtime, strftime, time

now = time()
print('now is', now)

local_tuple = localtime(now)
time_format = '%Y-%m-%d %H:%M:%S'
time_str = strftime(time_format, local_tuple)
print(time_str)

now is 1561372402.3313987
2019-06-24 19:33:22
# 현재 저녁 7시이다;
```

때로는 지역 시간으로 사용자 입력을 받아서 UTC 시간으로 변환하는 것처럼 반대로 처리해야 하는 경우도 있다. 이럴 때는 `strptime` 함수로 시간 문자열을 파싱한 후에 mktime으로 지역 시간을 유닉스 타임스탬프로 변환하면 된다.

```python
from time import mktime, strptime

time_tuple = strptime(time_str, time_format)utc_now = mktime(time_tuple)
print(utc_now)

1561372402.0
```

<br>

일단 단순 변환은 문제없이 동작한다. 하지만 한 시간대의 지역 시간을 다른 시간대의 지역 시간으로 변환하고 싶다고 할 때는 이야기가 다른다.

**time, localtime, strptime 함수의 반환 값을 직접 조작해서 시간대를 변환하는 건 좋지 못한 생각이다.** 시간대는 지역 규칙에 따라 모든 시간을 변경한다. 이 과정은 직접 처리하기엔 너무 복잡하며, 특히 전세계 모든 도시의 비행기의 출발, 도착 시간을 처리한다면 더욱 복잡해진다.

많은 운영체제에서 시간대 변경을 자동으로 관리하는 설정 파일을 갖추고 있다. **문제는 플랫폼에 의존적인 time모듈의 특성이다.** 실제 동작은 내부의 C함수가 호스트 운영체제와 어떻게 동작하느냐에 따라 결정된다. 이와 같은 동작 때문에 파이썬의 time 모듈의 기능을 신뢰하기 어렵다.   

따라서 이런 목적으로는 time 모듈을 사용하지 말아야 한다. time을 사용해야 한다면 UTC와 호스트 컴퓨터의 지역 시간을 변환하는 목적으로만 사용해야 한다. 다른 형태의 변환에는 datetime 모듈을 사용해야 한다.

<br>

## 3. datetime과 pytz 모듈로 시간대 변환하기

파이썬에서 시간을 표현하는 두 번째 방법은 내장 모듈 datetime의 datetime 클래스를 사용하는 것이다. time 모듈과 마찬가지로 datetime은 UTC에서의 현재 시각을 지역 시간으로 변경하는 데 사용할 수 있다.

다음은 현재 시각을 UTC로 얻어와서 Asia, Seoul 지역 시간으로 변경하는 코드다.


```python
from datetime import datetime, timezone

now = datetime.now()
now_utc = now.replace(tzinfo=timezone.utc)
now_local = now_utc.astimezone()
print(now_local)

2019-06-25 05:16:37.479484+09:00
# 서울은 UTC 기준 +9임
```

datetime 모듈로도 지역 시간을 다시 UTC의 유닉스 타임스탬프로 쉽게 변경할 수 있다.


```python
time_str = '2019-06-24 20:18:30'
now = datetime.strptime(time_str, time_format)
time_tuple = now.timetuple()
utc_now = mktime(time_tuple)
print(utc_now)

1561375110.0
```

datetime 모듈은 time 모듈과 달리 한 지역 시간을 다른 지역 시간으로 신뢰성 있게 변경한다. 하지만 tzinfo 클래스와 관련 메소드를 이용한 시간대 변환 기능만 제공한다. 빠진 부분은 UTC 이외의 시간대 정의다.  

다행히도 파이썬 커뮤니티에서는 이 허점을 pypi에서 다운로드할 수 있는 pytz 모듈로 해결하고 있다. pytz는 필요한 모든 시간대에 대한 정의를 담은 전체 데이터베이스를 포함한다.

pytz를 효과적으로 사용하려면 항상 지역 시간을 UTC로 먼저 변경해야 한다. 그러고 나서 UTC 값에 필요한 datetime 연산(오프셋 지정 등)을 수행한다. 그런 다음 마지막 단계로 지역 시간으로 변환한다.

예를 들어 다음은 서울 기준 시간을 미국 샌프란시스코 기준시로 변환하는 코드다.

```python
import pytz

time_seoul = '2019-06-24 20:28:30'
naive_time = datetime.strptime(time_seoul, time_format)
seoul = pytz.timezone('Asia/Seoul')
localized = seoul.localize(naive_time)
utc_dt = pytz.utc.normalize(localized.astimezone(pytz.utc))

print(utc_dt)

2019-06-25 00:28:30+00:00
```

서울 로컬 시간을 표준시로 변경했으니 이를 사용해서 샌프란시스코 지역 시간으로 변환해보자.

```python
pacific = pytz.timezone("US/Pacific")
sf_dt = pacific.normalize(utc_dt.astimezone(pacific))
print(sf_dt)

2019-06-24 04:28:30-07:00
```

datetime과 pytz를 이용하면 이런 변환이 호스트 컴퓨터에서 구동하는 운영체제와 상관없이 모든 환경에서 동일하게 동작한다.


<br>

## 4. 핵심 정리

* 서로 다른 시간대를 변환하는 데는 time 모듈을 사용하지 말자.
* pytz 모듈과 내장 모듈 datetime으로 서로 다른 시간대 사이에서 시간을 신뢰성 있게 변환하자.
* 항상 UTC로 시간을 표현하고, 시간을 표시하기 전에 마지막 단계로 UTC 시간을 지역 시간으로 변환하자.
