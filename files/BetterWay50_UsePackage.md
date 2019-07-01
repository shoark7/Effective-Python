## Better Way 50. 모듈을 구성하고 안정적인 API를 제공하려면 패키지를 사용하자

#### 255쪽

* Created : 2019/07/01
* Modified: 2019/07/01

<br>

## 1. Package란?

프로그램의 코드가 커지면 자연히 코드의 구조를 재구성하기 마련이다. 예를 들면 큰 함수를 더 작은 함수로 분할한다. 자료구조를 헬퍼 클래스로 리팩토링하거나 기능을 서로 의존적인 여러 모듈로 분할하기도 한다.

언젠가는 너무 많은 모듈이 있어서 모듈들을 이해하기 쉽게 하려고 프로그램에 다른 계층을 추가해야 하는 시점이 온다. 파이썬은 이런 목적으로 Package(이하 "패키지")를 제공한다. 패키지란 쉽게 말해 **다른 모듈들을 포함하는 모듈이다.**

패키지를 만드는 방법은 간단하다. **대부분은 디렉토리 안에 \_\_init\_\_.py 라는 빈 파일을 넣는 방법으로 패키지를 정의한다. \_\_init\_\_.py가 있으면 해당 디렉토리에 있는 다른 파이썬 파일은 디렉토리에 상대적인 경로로 임포트할 수 있다.**

예를 들어 프로그램의 디렉토리 구조가 다음과 같다고 하자.


> main.py  
> mypackage/\_\_init\_\_.py  
> mypackage/models.py  
> mypackage/utils.py  

이 구조에서 utils 모듈을 임포트하려면 패키지 디렉토리 이름을 포함하는 절대 모듈 이름을 사용해야 한다.

```python
# main.py

from mypackage import utils
```

패키지 디렉토리가 다른 패키지(예를 들면 mypackage.foo.bar) 안에 있을 때는 계속 이런 패턴을 따른다.

패키지가 제공하는 기능은 파이썬 프로그램에서 두 가지 주요 목적이 있다.


<br>

## 2. Package의 기능 1: 네임스페이스

**패키지의 첫 번째 용도는 분리된 네임스페이스(namespace)로 모듈들을 분할하는 것이다.** 이 기능은 파일 이름이 같은 여러 모듈이 서로 다른 절대경로를 갖게 해준다. 예를 들어 다음은 이름이 utils.py로 같은 두 모듈에서 각각 속성을 임포트하는 프로그램이다. 모듈을 단순 이름이 아닌 각각의 절대경로로 접근하므로 이름 충돌이 일어나지 않는다.


```python
# main.py
from analysis.utils import log_base2_bucket
from frontend.utils import stringify

bucket = stringify(log_base2_bucket(33))
```

디렉토리 안에 utils.py 라는 모듈이 동시에 존재하지만 패키지 구조 안에서 다른 절대경로를 갖기 때문에 충돌이 일어나지 않았다.

이 방법은 패키지에서 정의한 함수, 클래스, 서브모듈의 이름들이 같을 때는 동작하지 않는다. 예를 들어 analysis.utils와 frontend.utils 모듈에 있는 inspect 함수를 사용하고 싶다고 하자. 속성을 직접 임포트하면 두 번째 import문이 현재 영역에 있는 insepct의 값을 덮어쓰기 때문에 제대로 동작하지 않는다.


```python
# main2.py
from analysis.utils import inspect
from frontend.utils import inspect # 윗 줄의 inspect를 덮어씀!
```

이런 상황에서 해결책은 `as` 키워드를 사용하여 현재 영역에 임포트하는 대상의 이름을 변경하는 것이다.

```python
from analysis.utils import inspect as analysis_inspect
from frontend.utils import inspect as frontend_inspect

value = 33
if anaylysis(value) == frontend_insepct(value):
    print('Inspection equal!')
```

많이 써봤을 `as` 키워드는 import 문으로 임포트한 대상의 이름을 변경하는 데 사용한다. 모듈도 가능하다. as 키워드를 사용하면 네임스페이스가 붙은 코드에 접근하기 쉽고 대상을 사용할 때 실체를 명확하게 인식할 수 있다.

<br>


## 3. Package의 기능 2: 안정적인 API

파이썬에서 패키지의 두 번째 용도는 외부 사용자에게 명확하고 안정적인 API를 제공하는 것이다.  

오픈소스 패키지처럼 다양하게 사용할 목적으로 API를 작성할 때 릴리스 간의 변경 없이 안정적인 기능을 제공하고 싶다고 하자. 그러려면 **외부 사용자에게서 내부 코드 구조를 숨겨야 한다.** 이렇게 해두면 기존 사용자의 코드를 망가뜨리지 않고 패키지의 내부 모듈을 리팩토링하고 개선할 수 있다.

**파이썬에서는 모듈이나 패키지에 \_\_all\_\_ 이라는 특별한 속성으로 API 사용자에게 드러나는 외부영역을 제한한다. \_\_all\_\_의 값은 공개 API의 일부로 외부에 제공하려는 문자열 형태의 모듈 이름을 모두 담은 리스트다. 패키지를 사용하는 코드에서 `from foo import *`를 실행하면 foo 패키지의 모든 기능들이 임포트되는 것이 아닌, `foo.__all__`에 있는 속성만 import된다. 'foo'에 \_\_all\_\_이 없으면 속성 이름이 밑줄로 시작하지 않는 공개 속성만 임포트된다.**

예를 만들어보자. 움직이는 발사체 간의 충돌을 계산하는 패키지를 제공한다고 하자. 다음은 mypackage의 models 모듈을 정의하여 발사체를 표현하는 코드다.

```python
# models.py
__all__ = ['Projectile',]


class Projectile:
    def __init__(self, mass, velocity):
        self.mass = mass
        self.velocity = velocity
```

또한 mypackage에 utils 모듈을 정의하여 Projectile 인스턴스로 발사체 간의 충돌을 시뮬레이트하는 동작을 수행한다.

```python
# utils.py
from . models import Projectile

__all__ = ['simulate_collision',]

def _dot_product(a, b):
    pass

def simulate_collision(a, b):
    pass
```

이제 **두 모듈의 공개 API를 모두 mypackage 모듈에서 바로 사용 가능한 속성의 집합으로 제공하려고 한다.** 이렇게 하면 mypackage.models 혹은 mypackage.utils에서 임포트하는 대신, mypackage로부터 항상 직접 임포트할 수 있다. 이 방식은 mypackage의 내부 구조를 변경(예를 들면 models.py가 삭제되는 경우)하더라도 API를 사용하는 코드가 계속 동작함을 보장한다.

**파이썬 패키지로 이렇게 동작하게 하려면 mypackage 디렉토리에 있는 \_\_init\_\_.py 파일을 수정해야 한다.** 이 파일은 실제로 임포트될 때 mypackage 모듈의 내용이 된다. 따라서 \_\_init\_\_.py로 임포트하는 것을 제한하여 mypackage의 API를 명시적으로 설정할 수 있다. 이미 두 내부 모듈은 \_\_all\_\_을 명시하고 있으므로, 단순히 내부 모듈에서 모든 것을 임포트하고 \_\_init\_\_.py 모듈의 \_\_all\_\_ 속성을 이에 맞춰 업데이트하면 mypackage의 공개 인터페이스를 외부에 드러낼 수 있다.


```python
# __init__.py
from . models import *
from . utils import *

__all__ = []
__all__ += models.__all__
__all__ += utils.__all__
```

다음은 API의 사용자가 내부 모듈에 접근하지 않고 mypackage로부터 기능을 직접 임포트하는 코드다.


```python
# api_consumer.py
from mypackage import *

a = Projectile(1.5, 3)
b = Projectile(4, 1.7)
after_a, after_b = simulate_collision(a, b)
```

**위의 코드에서 사용한 Projectile이나 simulate\_collision은 원래 mypackage 내부에 있는 모듈에 포함된 속성들이다. 하지만 패키지의 \_\_init\_\_.py 파일에서 기능들을 직접 임포트함으로써 패키지 수준에서 기능을 끌어다쓸 수 있었다.**

**이때 기억할 것은 mypackage.utils.\_dot\_product 같은 내부 전용 함수는 \_\_all\_\_에 포함되지 않으므로 mypackage API 사용자는 사용할 수 없다는 것이다.** \_\_all\_\_에서 빠진다는 것은 `from mypackage import *` 문으로 임포트되지 않음을 의미한다. 따라서 내부 전용 이름을 효과적으로 숨길 수 있다.  

이런 모든 방법은 명시적이고 안정적인 API를 제공해야 할 때 잘 동작한다. 하지만 직접 만든 모듈 사이에서 사용하려고 API를 구축한다면 \_\_all\_\_ 기능이 필요 없을 것이므로 사용하지 말아야 한다. 패키지가 제공하는 네임스페이스는 의미 있는 인터페이스를 유지하며 많은 양의 코드로 협업하는 개발팀에도 일반적으로 충분한다.


<br>

## 4. 핵심 정리

* 파이썬의 패키지는 다른 모듈을 포함하는 모듈이다. 패키지를 이용하면 고유한 절대 모듈 이름으로 코드를 분리하고, 충돌하지 않는 네임스페이스를 구성할 수 있다.
* 간단한 패키지는 다른 소스 파일을 포함하는 디렉토리에 \_\_init\_\_.py 파일을 추가하는 방법으로 정의한다. \_\_init\_\_.py를 제외한 파일들은 디렉토리 패키지의 자식 모듈이 된다. 패키지 디렉토리는 다른 패키지를 포함할 수도 있다.
* \_\_all\_\_ 이라는 특별한 속성에 공개하려는 이름을 나열하여 모듈의 명시적인 API를 제공할 수 있다.
* 공개할 이름만 패키지의 \_\_init\_\_.py 파일에서 임포트하거나 내부 전용 멤버의 이름을 밑줄로 시작하게 만들면 패키지의 내부 구현을 숨길 수 있다.
* 단일 팀이나 단일 코드베이스로 협업할 때는 외부 API용으로 \_\_all\_\_을 사용할 필요가 없을 것이다.
