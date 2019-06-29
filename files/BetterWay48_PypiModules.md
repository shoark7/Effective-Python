## Better Way 48. 커뮤니티에서 만든 모듈을 어디서 찾아야 하는지 알아두자

#### 247쪽

* Created : 2019/06/29
* Modified: 2019/06/29

<br>

## 1. PyPI를 통한 패키지 설치

파이썬에는 설치 후 프로그램에서 사용할 수 있는 모듈들의 [중앙 저장소](https://pypi.org/)가 있다. 나와 여러분 같은 사람들, 즉 파이썬 커뮤니티에서 이러한 모듈을 만들고 관리한다. 파이썬 패키지 인덱스(PyPI, Python Package Index)는 여러분이 원하는 목적에 가까운 코드를 찾을 수 있는 좋은 방법이다.

패키지 인덱스를 사용하려면 명령줄 도구 `pip`을 사용해야 한다. pip은 파이썬 3.4와 그 이후 버전에는 기본적으로 설치되어 있다. 파이썬 3.4 이전 버전에서는 파이썬 패키징 웹사이트([packaging.python.org](https://packaging.python.org/))에서 pip 설치 설명서를 찾아보면 된다.  

일단 설치한 후에는 pip으로 새 모듈을 설치하는 방법은 간단하다. 예를 들어 'Better way 45'에서 사용한 pytz 모듈을 설치한다고 하자.

```sh
$ pip3 install pytz


Collecting pytz
  Using cached https://files.pythonhosted.org/packages/3d/73/fe30c2daaaa0713420d0382b16fbb761409f532c56bdcc514bf7b6262bb6/pytz-2019.1-py2.py3-none-any.whl
Installing collected packages: pytz
Successfully installed pytz-2019.1
```

위와 같은 방법으로 서드파티 모듈을 손쉽게 설치할 수 있다. 구체적인 결과는 나와 다를 수 있다. 나는 이미 설치되어 있었기 때문에 캐시된 곳에서 바로 받아올 수 있었다.

<br>

이 예에서는 ㅍ패키지의 파이썬 3버전을 설치하려고 pip3 명령을 사용했다. 많은 경우에 컴퓨터에 파이썬 2와 파이썬 3가 동시에 설치되어 있을 수 있다. 이때 pip 대신 `pip3`을 통해 모듈을 설치하면 파이썬 3에 명시적으로 모듈이 설치된다. 인기 있는 패키지의 대다수는 파이썬 버전 2, 3에서 모두 사용할 수 있다. 

**프로젝트별 가상환경 관리는 매우 중요한데 파이썬에서는 [pyenv](https://www.google.com/search?q=pyenv&oq=pyenv&aqs=chrome..69i57j0l5.630j0j7&sourceid=chrome&ie=UTF-8)를 많이 사용한다.** 나도 여기에 더해 [pipenv](https://docs.pipenv.org/en/latest/)까지 사용하고 있다.

PyPI의 각 모듈에는 자체의 소프트웨어 라이센스가 있다. 대부분의 패키지와 특히 인기 있는 패키지는 무료 또는 오픈소스다. 대부분의 경우 이런 라이센스는 프로그램에 모듈의 복사본을 포함하는 것을 포함한다.

<br>

## 2. 핵심 정리

* 파이썬 패키지 인덱스(PyPI)는 파이썬 커뮤니티에서 만들고 유지하는 풍부한 공통 패키지를 유지하고 있다.
* pip은 PyPI에서 패키지를 설치하는 데 사용하는 명령줄 도구다.
* pip은 파이썬 3.4와 그 이후 버전에는 기본으로 설치되어 있다. 이전 버전에서는 직접 설치해야 한다.
* PyPI 모듈의 대부분은 무료이자 오픈 소스 소프트웨어다.
