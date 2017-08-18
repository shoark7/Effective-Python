# Better way 56. unittest로 모든 것을 테스트하자


#### 289쪽
#### 2017/08/18 작성

파이썬에는 정적 타입 검사(Statically type checking) 기능이 없다.  
컴파일러는 프로그램을 실행하면 제대로 동작함을 보장하지 않는다.  
파이썬으로는 프로그램에서 호출하는 함수가 런타임에 정의되어 있을지 알 수 없기도 하다.  
(정적, 동적 타입검사에 대해서는 이 [포스트](https://thesocietea.org/2015/11/programming-concepts-static-vs-dynamic-type-checking/)를 참고.)  

파이썬은 동적 타입 검사하는 언어이기 때문에 더더욱 code test가 필요하다.  
좀 더 극단적으로 말해 파이썬 프로그램을 신뢰할 수 있는 유일한 방법은 직접 테스트를 작성하는 것이다.  

많은 경우 우리는 테스트를 하지 않으며 시간 낭비라고 생각하기도 한다.  
하지만 내가 나 혼자 쓰는 프로그램 이상의 가치를 만들고 싶다면 테스트는 꼭 필요하다.  
많은 기라성 같은 프로그래머가 강조하는 바이며 나는 'TDD를 하지 않는 회사는 들어가지 마라'고  
이야기하는 개발자를 보기도 했다.  

지금 소개하는 [unittest](https://docs.python.org/3/library/unittest.html) 내장 모듈은 코드 테스트를 위한 모듈로  
파이썬에서 테스트하는 가장 간단한 방법이기도 하다. 그리고 이 코드는 장고에서 지원하는 테스트 모듈과 비슷해서  
공부하면 도움이 될 것이다.

간단한 예제를 보도록 하자.

```python
# Utility function to test

def to_str(data):
    if isinstance(data, str):
        return data
    elif isinstance(data, bytes):
        return data.decode('utf-8')
    else:
	raise TypeError('Must supply str or bytes, '
	                'found: %r' % data)
```

<br>

이 함수를 테스트할 코드를 작성해보자.


```python
from unittest import TestCase, main

class ToStrTestCase(TestCase):
    def test_to_str_bytes(self):
        self.assertEqual('hello', to_str(b'hello'))
    
    def test_to_str_str(self):
        self.assertEqual('hello', to_str('hello'))

    def test_to_str_str_bad(self):
        self.assertRaises(TypeError, to_str, object())


if __name__ == '__main__':
    main()
```

테스트 코드를 작성하는 가장 대표적인 방식이다.  
테스트 코드들을 담을 테스트 클래스는 unittest의 **TestCase를 상속 받아야 한다.**  
그 안에 내가 테스트하고 싶은 함수들을 작성하는데, 그 함수들은 모두 **'test'로 시작해야 한다.**  
'test'로 시작하지 않은 메소드는 테스트할 코드로 인식하지 않으며  
이런 경우는 테스트 함수들에서 사용할 헬퍼 메소드를 작성한다면 좋을 것이다.  

테스트 메소드가 어떤 종류의 Exception을 일으키지 않고 실행된다면 테스트가 성공적으로 통과한 것이며  
TestCase 클래스는 테스트에서 단정하는 데(assert) 필요한 헬퍼 메소드를 지원한다.  
위 코드에서 동등성을 검사하는 assertEqual, 의도한 예외가 발생했는지 검사하는 asssertRaises 등이다.  
TestCase 서브클래스에 자신만의 헬퍼 메소드를 정의하여 맞춤형 테스트를 만들 수도 있을 것이다.  
물론 그 헬퍼 메소드는 'test'로 시작해서는 안 된다.

<br>

때때로 TestCase 클래스에서 테스트 메소드를 실행하기 전에 테스트 환경을 설정해야 한다.  
그러려면 setUp과 tearDown 메소드를 오버라이드 해야 한다.  
이 메소드들은 각 테스트 메소드가 실행되기 전후에 각각 호출되며, 각 테스트가 분리되어 실행됨을 보장한다.  

예를 들어 다음 코드는 각 테스트 전에 임시 디렉토리를 생성하고, 각 테스트가 종료한 후에 그 내용을 삭제하는  
TestCase를 정의한 것이다.

```python
from tempfile import TempDirectory

class MyTest(TestCase):
    def setUp(self):
        self.test_dir = TemporaryDirectory()

    def tearDown(self):
        self.test_dir.cleanup()

    # ... 테스트 메소드
```

보통 관련 테스트의 각 집합별로 TestCase 하나를 정의한다.  
때로는 예외 상황이 많은 각 함수별로 만들 수도 있고, 한 케이스로 모듈 내 모든 함수를 처리하기도 한다.  
이는 프로그래머의 판단이며 가독성 있고 이해하기 쉽게 구분하여 테스트하면 좋을 것이다.  

프로그램이 복잡해지면 코드를 별도로 테스트하는 대신에 모듈 간의 상호작용을 검증할 테스트를 추가할 수도 있다.  
이게 바로 단위 테스트(unittest)와 통합 테스트(integration test)의 차이다.  
파이썬에서는 똑같은 이유로 두 종류의 테스트를 작성해야 한다.  
모듈을 검증하지 않으면 실제로 함께 동작하는지 보장하지 못하기 때문이다.

테스트를 위한 서드파티 패키지도 물론 존재한다.  

[pytest](https://docs.pytest.org/en/latest/)는 unittest 코드도 동작하는 호환성을 보장하며  
프로젝트도 성숙해서 믿고 사용할 수 있다고 한다. 기능이 더 강력한 것은 당연한다.  
Pycon 2017 kr의 한 강연에서도 테스트를 설명하면서 pytest를 홍보하기도 했다.  
pytest를 쓰면 unittest를 아예 쓸 일이 없다고 한다. 강력한 모듈인 것은 확실한 것 같다.  

<br><br>

### 핵심정리
* 파이썬 프로그램을 신뢰할 수 있는 유일한 방법은 테스트를 작성하는 것이다.
* 내장 모듈 unittest는 좋은 테스트를 작성하는 데 필요한 대부분의 기능을 제공한다.
* TestCase를 상속하고 테스트하려는 동작별로 메소드 하나를 정의해서 테스트를 정의할 수 있다.
TestCase 클래스에 있는 테스트 메소드는 'test'라는 단어로 시작해야 한다.
* 단위 테스트와 통합 테스트는 상호 보완적이므로 모두 작성해야 한다.
