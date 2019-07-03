## Better Way 53. 의존성을 분리하고 재현하려면 가상환경을 사용하자

#### 273쪽

* Created : 2019/07/03
* Modified: 2019/07/03

<br>


## 1. 전역 라이브러리 관리의 문제점

더 크고 복잡한 프로그램을 구축할 때는 파이썬 커뮤니티에서 만든 다양한 패키지를 사용하기 마련이다.(ex: Django, Flask) 결국 pip을 사용해 이들을 설치하는 자신을 발견하게 될 것이다.

문제는 **pip이 기본으로 새 패키지를 전역 위치에 설치한다는 점이다.** 그래서 시스템에 있는 모든 파이썬 프로그램이 설치된 모듈의 영향을 받는다. 이론적으로는 이게 문제가 되지 않는다. 패키지를 설치하고 임포트하지 않는다면 프로그램에 어떻게 영향을 미칠 수 있을까?

문제는 `의존성 전이`(transitive dependencies), 즉 설치한 패키지가 의존하는 패키지 때문에 생긴다. 예를 들어 소프트웨어 문서화 도구인 [Sphinx](http://www.sphinx-doc.org/en/master/) 패키지를 설치한 후 pip을 통해 Sphinx가 어떤 패키지에 의존하는지 알 수 있다.

```shell
$ pip show Sphinx

name: Sphinx
Version: 2.1.2
# 생략...
Location: /home/sunghwanpark/.local/share/virtualenvs/test-dependency-2VwzX83x/lib/python3.6/site-packages
Requires: Jinja2, sphinxcontrib-devhelp, sphinxcontrib-qthelp, docutils, # 너무 길어 생략
Required-by:
```

마찬가지로 파이썬 웹 마이크로 프레임워크인 [flask](http://flask.pocoo.org/)에도 같은 작업을 할 수 있다.

```Name: Flask
Version: 1.0.3
# 생략...
Location: /home/sunghwanpark/.local/share/virtualenvs/test-dependency-2VwzX83x/lib/python3.6/site-packages
Requires: click, Jinja2, Werkzeug, itsdangerous
Required-by: shell
```

**이 둘 모듈에서 공통점은 모두 'Jinja2'라는 라이브러리에 의존하고 있다는 점이다.**

**충돌은 시간이 지남에 따라 Sphinx와 flask가 의존하는 버전이 갈리면서 일어난다.** 아마 지금은 둘 다 같은 버전의 Jinja2를 요구해서 모든 게 괜찮을지도 모른다. 하지만 6개월 뒤나 1년 후에는 Jinja2는 라이브러리 사용자의 기능을 망가뜨리는 변경을 적용한 새로운 버전을 릴리스할 수도 있다. 이때 `pip install --upgrade` 명령으로 Jinja2의 전역 버전을 업데이트하면 flask는 동작하지만 Sphnix는 제대로 동작하지 않을지도 모른다.

이런 문제의 원인은 파이썬이 전역 버전 모듈을 한 번에 하나만 두기 때문이다. 설치한 패키지 중 하나는 새로운 버전을 사용해야 하고 다른 패키지는 이전 버전을 사용해야 한다면 시스템이 제대로 동작하지 않을 것이다.

이런 문제는 패키지 유지보수 작업자가 릴리스 간에 API 호환성을 유지하려고 할 때도 발생한다. 라이브러리의 새로운 버전은 API를 사용하는 코드가 의존하는 동작을 약간 변경할 수도 있다. 시스템 사용자들이 패키지 하나를 새로운 버전으로 업그레이드하고 나머지는 업그레이드하지 않으면 의존성이 깨진다. 그러면 끊임없이 위험이 따른다.

**이러한 어려움은 서로 분리된 로컬 컴퓨터에서 작업하는 다른 개발자들과 협력할 때 더 커진다.** 보통 머신마다 파이썬 버전과 설치한 패키지의 버전이 서로 약간씩이라도 다르다고 생각하는 것이 합리적이기 때문이다. 이런 차이 때문에 코드베이스가 한 프로그래머의 머신에서는 완벽하게 실행되지만 다른 사람의 머신에서는 완전히 망가지는 실망스러운 상황이 생긴다.  

<br>

## 2. 해결책: 가상환경을 통한 프로젝트별 패키지 관리

이런 모든 문제의 해결책은 가상환경(virtual enviroment)을 제공하는 도구를 사용하는 것이다. 여기서는 파이썬의 내장 도구를 살펴본다. 다른 해결책은 [pyenv](https://github.com/pyenv/pyenv), [pipenv](https://docs.pipenv.org/en/latest/) 등이 있지만 여기서 사용할 pyvenv는 3.4 버전 이후부터 설치없이 사용할 수 있어서 살펴볼만하다. 이전 버전에서는 `pip install virtualenv`로 별도의 패키지를 설치한 후 `virtualenv` 명령줄 도구로 사용해야 한다.

`pyvenv`는 독립된 버전의 파이썬 환경을 생성할 수 있게 해준다. **pyvenv를 이용하면 같은 시스템에서 같은 이름으로 설치된 패키지의 여러 버전을 충돌없이 사용할 수 있다.** 이 방법으로 같은 컴퓨터에서 서로 다른 여러 프로젝트에서 작업하고 많은 도구를 쓸 수 있다.

**`pyvenv`는 명시적인 버전의 패키지들과 의존 패키지들을 완전히 분리된 디렉토리 구조로 설치하여 독립된 환경을 구성한다.** 덕분에 코드에 알맞은 파이썬 환경을 재현할 수 있다. 이런 가상환경 구성은 앞에서 다룬 뭄ㄴ제를 피하는 올바른 방법이다.

<br>

pyvenv를 사용해보자. 먼저 로컬 컴퓨터에 설치된 전역 파이썬의 버전과 프로그램의 위치를 살펴보자.

```shell
# 전역 파이썬 위치 확인
# 구체적인 값은 머신마다 다름
$ which python

/home/sunghwanpark/.pyenv/shims/python
```

```shell
# 전역 파이썬 버전 확인
# 구체적인 값은 머신마다 다름
$ python --version

3.6.3.
```

전역 파이썬의 위치와 버전을 확인했다. 이는 이후 `pyvenv`를 사용하면서 디렉토리별, 즉 프로젝트별로 서로 다른 파이썬의 위치와 버전을 갖는 것을 확인하기 위해 출력했다.

또 전역 스코프에에 'pytz'라는 모듈이 설치되어 있는지도 확인한다.

```shell
$ python -c 'import pytz'

# (결과는 출력되지 않음)
```

python에 `-c` 옵션은 그 다음에 받는 문자열로 된 파이썬 코드를 실행하겠다는 의미이다. 지금은 단순히 'pytz' 모듈을 임포트만 하기 때문에 따로 출력물이 없었다. 단, 해당 모듈이 설치되어 있지 않았다면 에러가 발생했을 것이다. **즉, 현재 내 머신의 파이썬 전역 스코프에 'pytz' 모듈은 설치되어 있는 상태다.**

<br>

이제 pyvenv를 사용해서 myproject라는 새 가상환경을 생성해보자. **각 가상환경은 자신만의 독립적인 디렉토리에 있어야 한다.** 명령의 결과는 디렉토리와 파일의 트리 형태로 나타난다.

```shell
$ pyvenv /tmp/myproject
$ cd /tmp/myproject
$ ls

bin  include  lib  lib64  pyvenv.cfg
```

pyvenv 명령을 통해 하나의 프로젝트 단위가 되는 디렉토리를 생성했다. 그 안에는 미리 설정된 디렉토리와 파일들이 생성됐다. **가상환경을 시작하려면 쉘에서 source 명령으로 bin/activate 스크립트를 실행한다.** activate는 가상환경에 맞게 모든 환경변수를 수정한다. 또한 현재 무엇을 하고 있는지 확실히 알 수 있게 쉘 프롬프트를 수정하여 가상환경 이름('myproject')을 포함하게 한다.

```shell
$ source bin/activate

(myproject) $
# '$' 앞에 가상환경 이름이 붙었다.
```

가상환경을 시작하면 쉘에 따로 설정을 안 했다면 `$` 앞에 가상환경 이름이 붙는다. 이를 통해 **개발자는 현재 쉘이 전역 파이썬 스코프를 사용하지 않고 프로젝트별 가상환경(여기서는 'myproject')에 모듈을 설치하고, 사용할 것이라고 알 수 있다.** 참고로 `source`는 파이썬 명령어는 아니고, 유닉스 쉘의 쉘 스크립트를 실행시키는 명령어다. 'bin/activate'를 에디터로 확인해보면 쉘 명령어 모음을 확인할 수 있다.

이렇게 가상환경이 활성화되면 파이썬의 경로가 가상 환경 디렉토리로 이동했음을 알 수 있다.


```python
(myproject) $ which python

/tmp/myproject/bin/python
```

이는 외부 시스템에 대한 변경은 가상 환경에 영향을 미치지 않음을 보장한다. 외부 시스템이 기본 파이썬 버전을 3.7로 업그레이드하더라도 방금 만든 가상환경은 여전히 기존 버전을 유지한다.

pyvenv로 생성한 가상환경은 pip과 setuptools 말고는 설치된 패키지가 없이 시작한다. 외부 시스템에 전역 모듈로 설치한 pytz 패키지를 사용하려고 하면 가상환경에서는 이 패키지가 설치되어 있지 않아 실패한다.

```shell
(myproject) $ python -c 'import pytz'

Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'pytz'
```

아까와 달리 'pytz'가 설치되어 있지 않다고 출력된다. 이는 가상환경과 전역환경이 서로 다른 환경을 유지한다는 증거이기도 하다. 이제 가상환경에 pytz 모듈을 설치해보자.

```shell
(myproject) $ pip install pytz
```

설치한 후에는 같은 테스트 임포트 명령으로 동작함을 알 수 있다.

```shell
(myproject) $ python -c 'import pytz'

# 에러가 출력되지 않음
```

<br>

**가상환경에 대한 작업을 완료하고 기본 시스템(전역 스코프)으로 돌아가려면 `deactivate` 명령을 실행하면 된다.** 이 명령은 python 명령줄 도구의 위치를 포함한 환경을 시스템 기본 환경으로 복원한다.


```python
(myproject) $ deactivate
$ which python

/home/sunghwanpark/.pyenv/shims/python
```

다시 가상환경으로 복귀하고 싶다면 이전과 마찬가지로 실행하면 된다.

<br>

## 3. 의존성 재현

가상환경을 갖추고 있다면 pip으로 필요한 패키지를 계속 설치할 수 있다. 언젠가는 이 환경을 다른 머신으로 복사하고 싶을 수 있다. 예를 들어 프로덕션 서버에 테스트 서버에서 관리하던 가상환경을 재현하고 싶다고 하자. 혹은 자기 머신에 다른 사람의 환경을 복사하여 다른 사람이 작성한 코드를 실행하고 싶을 수도 있다.

pyvenv를 위시한 다른 가상환경 프로그램에서는 이런 상황에 쉽게 대처할 수 있다. **`pip freeze` 명령을 사용하면 모든 명시적인 패키지 의존성을 파일에 저장할 수 있다. 관례상 이 파일의 이름은 `requirements.txt`로 지정한다.** 이 파일은 기억하면 좋은데, 여러 파이썬 git repository에서 많이 발견되기 때문이다.

```shell
(myproject) $ pip freeze > requirements.txt
(myproject) $ cat requirements.txt

pytz==2019.1
```

이제 다른 경로, 또는 다른 머신에서 이 가상환경을 그대로 복원한다고 하자. 이전과 마찬가지로 pyvenv로 새 디렉토리를 생성한 후 activate한다.

```shell
$ pyvenv otherproject
$ cd otherproject
$ source bin/activate
```

새로 만든 가상환경에는 기본 모듈 외에는 설치되어 있지 않다.

```
(otherproject) $ pip list

pip (9.0.1)
setuptools (28.8.0)
```

myproject에서 만든 **requirements.txt 파일을 `pip install`를 통해 실행해서 모든 패키지를 설치한다.**

```shell
(otherproject) $ pip install -r requirements.txt

# requirements.txt는 myproject에서 복사해왔다고 가정
```

해당 명령어를 입력하면 myproject의 모든 패키지를 원 버전에 맞게 완벽하게 설치할 수 있다. 저 명령어의 `-r` 옵션은 'recursive'의 약자로 requirements.txt에 나열되어 있는 모든 패키지를 반복적으로 설치하겠다는 뜻이 된다. 설치가 완료되면 프로젝트의 모든 환경이 다른 환경으로 완벽하게 복제할 수 있다.

**`requirements.txt`를 사용하면 버전 제어 시스템을 사용해 다른 사람들과 협력하기에 좋다.** 변경한 코드를 커밋할 때 패키지 의존성 목록이 수정되어 정확하게 변경됨을 보장할 수 있다.

<br>

## 4. 핵심 정리

* 가상환경은 pip를 사용하여 같은 머신에서 같은 패키지의 여러 버전을 충돌 없이 설치할 수 있게 해준다.
* 가상환경을 만드는 프로그램은 많지만 내장 pyvenv를 사용하면 추가 설치없이 가상환경을 관리할 수 있다.
* pip freeze로 환경에 대한 모든 요구 사항을 덤프할 수 있다. `requirements.txt` 파일을 `pip install -r` 명령의 인수로 전달하여 환경을 재현할 수 있다.
* 파이썬 3.4 이전 버전에서는 pyvenv 도구를 별도로 설치해야 했고 명령줄 도구의 이름도 pyvenv가 아닌 virtualenv다.
