## Better Way 54. 배포 환경을 구성하는 데는 모듈 스코프 코드를 고려하자

#### 282쪽

* Created : 2019/07/03
* Modified: 2019/07/03


<br>

## 1. 모듈 내 코드를 통한 환경 제어

배포 환경(deployment environment)은 프로그램을 실행하는 구성을 말한다. 모든 프로그램에는 적어도 하나의 배포 환경과 제품 환경roduction environment)이 있다. **프로그램을 작성하는 첫 번재 목적은 제품 환경에서 프로그램이 동작하도록 하고 결과를 얻는 것이다.**

프로그램을 작성하거나 수정하려면 개발에 사용 중인 컴퓨터에서 프로그램이 동작하게 해야 한다. 개발 환경(development environment)의 설정은 제품 환경과는 많이 다르다. 예를 들어 리눅스 워크스테이션으로 슈퍼컴퓨터용 프로그램을 작성할 수도 있다.

제품 환경과 개발 환경의 차이를 구분하는 것이 중요하다. **보통 제품 환경에서는 개발 환경에서 재현하기 어려운 많은 외부 기능을 요구하기 마련이다.**  

예를 들어 프로그램이 웹 서버 컨테이너에서 실행되고 데이터베이스에 접근해야 한다고 하자. 이는 프로그램의 코드를 수정할 때마다 서버 컨테이너를 실행해야 하고, 데이터베이스를 적절하게 설정해야 하며, 프로그램에는 접근용 패스워드가 필요함을 의미한다. 한 줄을 변경하더라도 프로그램이 올바르게 동작하는지 검증하는 일을 하려고 한다면 상당한 노력이 필요하다. **즉, 제품 환경과 개발 환경을 구분하는 것은 정말 중요하다.**  

이런 문제를 해결하는 가장 좋은 방법은 시작할 때 프로그램의 일부를 오버라이드해서 배포 환경에 따라 서로 다른 기능을 제공하는 것이다. 예를 들면, 서로 다른 \_\_main\_\_ 파일을 두 개 만들어둘 수도 있다. 하나는 제품용으로, 다른 하나는 개발용으로 사용할 수 있다.

```python
# dev_main.py, 개발용
TESTING = True
import db_connection
db = db_connection.Database()


# prod_main.py, 제품용
TESTING = False
import db_connection
db = db_connection.Database()
```

이 두 파일의 유일한 차이점은 TESTING 상수의 값뿐이다. 프로그램에서 다른 모듈들은 \_\_main\_\_ 모듈을 임포트하고 TESTING 값으로 자체의 속성을 정의하는 방법을 결정한다.

```python
# db_connection.py

import __main__

class TestingDatabase:
    pass


class RealDatabase:
    pass

if __main__.TESTING:
    Database = TestingDatabase
else:
    Database = RealDatabase
```

여기서 알아야 할 중요한 동작은 **(함수나 메소드 내부가 아닌) 모듈 스코프에서 동작하는 코드는 일반 파이썬 코드라는 점이다.** 모듈 수준에서 if 문을 이용하여 모듈이 이름을 정의하는 방법을 결정할 수 있다. 이 방법으로 모듈을 다양한 배포 환경에 알맞게 만들 수 있다. 또한 데이터베이스 설정 등이 필요 없을 때 재현해야 하는 수고를 덜 수 있다. 목(mock)이나 가짜 구현을 주입하여 대화식 개발과 테스트를 용이하게 할 수도 있다.

<br>

이 방법을 외부의 전제를 우회하는 목적 이외에도 사용할 수 있다. 예를 들어, 프로그램이 호스트 플랫폼에 따라 다르게 동작해야 한다면 모듈의 최상위 구성요소를 정의하기 전에 `sys` 모듈을 조사하면 된다.

```python
# db_connection.py
import sys

class Win32Database:
    pass


class PosixDatabase:
    pass


if sys.platform.startswith('win32'):
    Database = Win32Database
else:
    Database = PosixDatabase
```

이와 유사하게 os.environ에 들어 있는 환경변수를 기반으로 모듈을 정의할 수도 있다.


<br>

## 2. 핵심 정리

* 종종 프로그램을 여러 배포 환경에서 실행해야 하며, 각 환경마다 고유한 전제와 설정이 있다.
* 모듈 스코프에서 일반 파이썬 문장을 사용해서 모듈 컨텐츠를 다른 배포 환경에 맞출 수 있다.
* 모듈 컨텐츠는 'sys'와 'os' 모듈을 이용한 호스트 조사 내역 같은 외부 조건의 결과물이 될 수 있다.
