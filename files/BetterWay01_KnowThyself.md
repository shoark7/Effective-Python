# Better way 1. 사용 중인 파이썬의 버전을 알자


#### 16쪽
#### Created : 2018/01/11
#### Modified: 2019/05/03


## 1. 사용하는 파이썬의 버전을 왜 알아야 할까?

프로그램은 개발자들에 의해 유지, 보수된다. 버전업될 때마다 여러 기능이 추가되거나 삭제되며,  
특히 파이썬 2에서 3으로의 변화같이 프로그램의 상당 부분이 바뀌는 경우도 다분하다.  
특정 파이썬 2코드가 파이썬 3에서 에러를 출력하는 경우가 꽤나 많다.  

다른 개발자와 협업할 때, 버전이 다른 프로그램을 쓰는 것은 일반적으로 용납되지 않는다.  
서로 같은 코드에서 결과물이 다를 수 있고, 이럴 때 다른 버전을 쓴다는 것을 인지하지 못하면  
디버깅이 산으로 갈 수 있다. 협업하는 개발자들과는 같은 버전의 프로그램을 써야 하고,  
그렇기 때문에 우리가 `requirements.txt` 등으로 같은 버전의 패키지를 쓰려고 하는 것일테다.  

같은 버전의 프로그램을 쓰기 위해서는 내 버전을 알아야 하고,  
그래서 파이썬에서 버전을 어떻게 확인하는지 아는 것도 의미가 있다.


<br>


## 2. 버전을 실제로 알아보자.

파이썬에서 버전을 확인해볼 수 있는 방법은 다음과 같다.

### 2.1. CLI에서 버전 인자를 통해 확인하기

이는 파이썬뿐만 아니라 다른 프로그램들에서도 일반적인 경우이다.  
우리는 `python` 이라는 명령어를 입력하고 파이썬 인터프리터를 실행하는데(CLI에서),  
알다시피 다양한 옵션을 줄 수 있다. 이때 파이썬의 버전을 확인할 수 있는 옵션은 다음 두 가지이다.

<br>

```sh

python --version
python -V


>>> Python 3.5.2
```

둘은 완벽히 같은 결과를 낸다. 두 번째 `V`는 대문자이다.  
이 명령어를 통해 파이썬 버전이 3.5.2라는 것을 확인했다.  

한 가지 기억해둘건, 이 방법은 비단 파이썬에만 해당하는 내용은 아니라는 것이다.  
수많은 프로그램의 버전을 위와 같은 방법을 통해 확인할 수 있다.  
예를 들어 리눅스에서 가장 많이 쓰는 기능 중 하나일 `ls`도 **결국 다른 사람이 만든 프로그램이고,**  
이 프로그램의 버전을 위와 같은 방법으로 확인할 수 있다.


```sh
ls --version


>>> ls (GNU coreutils) 8.25
Copyright (C) 2016 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

Richard M. Stallman 및 David MacKenzie이(가) 만들었습니다.
```

난 처음에 `ls`가 명령어라고만 생각했지, 프로그램이라고는 생각 못했다.  
이 방법은 기억해둘만 하다. 수많은 프로그램들에서 공통으로 쓸 수 있는 인자들이 여럿 있다.  
대표적으로는 프로그램의 사용법을 확인하는 `--help` 등도 있다.  

참고로 리눅스 프로그램에서 `--version`이 일반적이고 `-V`는 그렇지는 않다. `ls`에서는 이 인자를 받지
않는다.  


<br>
<br>


## 2.2. sys 모듈을 사용하기

버전을 확인하는 다른 방법은 파이썬의 내장 모듈 `sys`를 사용하는 것이다.  
이 모듈에는 파이썬의 버전을 출력해주는 특성이 두 개 있다.  

하나는 `sys.version`으로 파이썬 버전을 문자열로 출력해준다.  

<br>

```python
import sys

print(sys.version)


>>> 3.5.2 (default, Jul 10 2017, 10:43:13)
[GCC 5.4.0 20160609]
```

`sys.version`는 순수한 문자열이다.  

또 다른 방법은 `sys.version_info`를 사용하는 것이다.  
이런 경우가 있을 수 있다. 파이썬 코드로 파이썬 프로그램을 실행하는데,  
파이썬 버전에 따라 실행하는 코드를 다르게 한다고 하자.  

파이썬 2와 3일 때를 구분해야 하는데, `sys.version`을 쓴다면 이 문자열을 슬라이싱하려고 할 것이다.  
근데 그것뿐만 아니라 '3.2'인지, '3.6'인지도 구분해야 한다면 슬라이싱이 보다 복잡해질 것이다.  
그때 `sys.version_info`를 쓴다.  

<br>

가령 '3.5.2'라는 버전에서 '.'을 사이로 각 버전 정보가 구분되는데,

* 3은 major
* 5는 minor
* 2는 micro

라고 .불린다. `version_info`는 [named tuple](https://docs.python.org/3/library/collections.html#collections.namedtuple){:target="_blank"}로서,  **major, minor, micro라는 key로 각 숫자에 접근할 수 있다.**  
자세히 살펴보면 다음과 같다.  


```python
import sys

sys.version_info

sys.version_info.major
sys.version_info.minor
sys.version_info.micro


>>> sys.version_info(major=3, minor=5, micro=2, releaselevel='final', serial=0)
>>> 3
>>> 5
>>> 2
```

위와 같은 방법으로는 파이썬 프로그램의 major, minor, micro 버전 값을 정확하고 쉽게 파악할 수 있다.


<br>
<br>
<br>


#### 핵심정리

* 파이썬에는 CPython, Jython, PyPy 같은 다양한 런타임이 있다.
* 특히 협업 프로젝트에서 팀원이 같은 파이썬 버전을 사용하는 것은 매우 중요하다.
* 파이썬 2는 유지보수 정도의 지원만 남아있다. 이제는 2버전은 곧 지원이 종료되기 때문에 갈아타자.
