# Better way 49. 모든 함수, 클래스, 모듈에 docstring을 작성하자.


#### 250쪽
#### 2017/08/16 작성

<br>

## Part 1. docstring이란?
파이썬에서 문서화는 언어의 동적 특성 때문에 매우 중요하다.  
파이썬은 코드 블록에 문서를 첨부하는 기능을 기본적으로 지원한다.  
파이썬은 다른 언어들과 달리 프로그램 실행 중에 소스 코드에 첨부한  
문서에 직접 접근할 수 있다.  


이를 우리는 **docstring**이라고 부르며 이에 대한 정의는

> 모듈, 함수, 클래스, 메소드 정의에 처음 나타나는 문자열 상수.  
> docstring은 그 객체들의 \_\_doc\_\_라는 특수한 속성이 된다.
>
> [PEP 257](https://www.python.org/dev/peps/pep-0257/) 발췌

<br>


예를 한 번 살펴보자.  
함수의 def 문 바로 다음에 docstring을 직접 작성하여 문서를 추가할 수 있다.  

```python
def palindrome(word):
    """Return True if the given word is a palindrome."""
    return word == word[::-1]

```

<br>

함수의 \_\_doc\_\_이라는 특별한 속성에 접근하면 파이썬 프로그램 자체에 포함된 docstring을 확인할 수 있다.

```python
print(repr(palindrome.__doc__))


>>>
'Return True if the given word is a palindrome.'
```

<br>
이는 함수나 클래스 등의 사용법이나 인터페이스 접근을 쉽게 한다.
docstring은 앞서 확인했듯이 클래스 등의 정의 바로 밑에 나타나는데,  
파이썬에서 여느 언어와 마찬가지로 문서화는 꽤나 중요한 위치에 놓여 있다.  

<br>

함수, 클래스 등에 공통으로 적용되는 docstring의 기본속성은 다음과 같다.  
* docstring은 언제나 """ """을 사용하며 #을 이용하지 않는다. # 뒤에 문장은 docstring으로 인식되지 않는다.
* docstring에 '\'(백슬래쉬)를 쓴다면 r""" for python 3 """, 또는 u""" for python 2 """와 같이 쓴다.
* docstring의 첫 문장은 언제나 명령문 형태를 사용하며 끝에는 '.'을 꼭 붙인다.  
예를 들어(Do this and something. : O  Calculate**s** something. : X)
* docstring이 여러 문장이라면 첫 문장을 쓰고 반드시 한 문장을 비우고 다음 문장을 잇는다.  
그래야 docstring을 파싱하는 모듈들에서 정상적으로 작동한다.

<br>

위 기본속성은 빙산의 일각이며 [PEP 257](https://www.python.org/dev/peps/pep-0257/)을 꼭 읽어보자.  
별로 길지도 않으며 어렵지도 않다.


docstring은 패키지, 모듈, 클래스, 함수, 메소드에 붙일 수 있다.  
이와 같은 연결은 파이썬 프로그램을 컴파일하고 실행하는 과정의 일부다.  
docstring과 \_\_doc\_\_ 속성을 지원하는 덕분에 다음 세 가지 효과를 얻는다.

1. 문서의 접근성 덕분에 대화식 개발이 쉽다. 내장 함수 help로 클래스 등을 조사하여 문서를 볼 수 있다.
따라서 파이썬 대화식 인터프리터(쉘이나 Ipython 노트북)과 같은 도구에서 여러 개발을
상대적으로 쉽게 할 수 있다.
2. 문서를 정의하는 표준 방법이 있으면 텍스트를 더 쉽게 이해할 수 있는 포맷(이를테면 HTML)으로
변환하는 도구를 쉽게 만들 수 있다. 그래서 Sphinx 같은 훌륭한 문서 생성 도구가 생겨났다.
3. 파이썬의 일급 클래스, 접근성, 잘 정리된 문서는 사람들이 문서를 더 많이 작성할 수 있도록 한다.
파이썬 커뮤니티의 멤버들은 문서화가 중요하다고 강하게 믿고 있다.
이는 대부분의 오픈 소스 파이썬 라이브러리가 잘 작성되 문서를 갖추고 있음을 의미한다.

<br>

그러니 우리 모두 PEP 257를 읽고 문서화를 생활화하도록 하자.

<br><br>


## Part 2. 문서화 방법
이번에는 함수, 클래스, 모듈, 패키지 순으로 각 객체의 문서화 tip에 대해 살펴본다.
<br>

### 2.1 함수 & 메소드 문서화
각 공개 함수와 메소드는 docstring이 필요하다.  
첫 번째 줄은 함수가 수행하는 일을 한 문장으로 설명한다. 그 다음 문단부터는  
함수의 특별한 동작이나, 인수에 대해 설명한다. 반환 값도 언급한다.  
호출하는 쪽에서 함수 인터페이스의 일부로 처리해야 하는 예외도 설명한다.


```python
def find_anagrams(word, dictionary):
    """Find all anagrams for a word.

    This function only runs as fast as the test 
    for membership in the 'dictionary' container. It will
    be slow if the dictionary is a list and fast if it's a set.
    
    Args:
        word: String of the target word.
	dictionary: Container with all strings that are known to be actual words.

    Returns:
        List of anagrams that were found. Empty if none were found.
    """
    Do something...
```

<br>
함수 docstring을 작성할 때 작성할 때 알아둬야 할 몇 가지 경우가 있다.

* 함수 docstring 뒤에 blank line을 쓰지 않는다. 바로 함수를 작성한다.
* 함수가 인자는 받지 않고 값만 반환하면 한 줄짜리 설명만으로 충분하다.
* 함수가 아무것도 반환하지 않으면 'return None' 대신 반환값을 언급하지 않는 것이 좋다.
* 함수가 일반적인 동작에서는 예외를 일으키지 않는다고 생각한다면 이에 대해서는 언급하지 않는다.
* 함수가 받는 인수의 개수가 가변적이거나 키워드 인자를 사용한다면,  
문서의 인수 목록에 \*args, \*\*kwargs를 사용해서 그 목적을 설명한다.
* 함수가 기본값이 있는 인수를 받으면 해당 기본값을 설명한다.
* 함수가 제너레이터라면 제너레이터가 순회할 때 무엇을 넘겨주는지 설명한다.
* 함수가 코루틴이라면 코루틴이 무엇을 넘겨주는지, yield 표현식으로부터 무엇을 얻는지,
언제 순회가 끝나는지를 설명한다.


<br>

### 2.2. 클래스 문서화
각 클래스는 클래스 수준의 docstring이 있어야 한다.  
첫 번째 줄은 클래스의 목적을 기술하는 한 문장으로 구성한다.  
그 이후의 문단에는 클래스의 동작과 관련한 중요한 내용을 기술한다.

클래스의 중요한 공개 속성과 메서드는 클래스 수준에서 강조해야 한다.  
또한 서브클래스가 보호 속성, 슈퍼클래스의 메서드와 올바르게 상호 작용하는 방법을 안내해야 한다.

클래스 docstring에서 몇 가지 특기할 사항은 다음과 같다.
* 클래스의 경우는 함수와 달리 docstring 작성 이후 blank line을 하나 넣는다.
* 서브 클래스에서 상속을 할 경우 override 단어를 사용한다. 그런데 슈퍼 클래스의 기능에 덧붙여
다른 기능이 단순히 추가되는 경우라면 **extend**라는 단어를 사용하는 것도 좋다.


```python
class Player:
    """Represent a player of the game.

    Subclasses may override the 'tick' method to provide
    custom animations for the player's movement depending
    on their power level, etc.

    Public attributes:
    - power: Unused power-ups(float between 0 and 1)
    - coins: Coins found during the level(integer)
    """

    Do something..
```

<br>
<br>

### 2.3 모듈 문서화
각 모듈은 최상위 docstring을 가지고 있어야 한다. 최상위 docstring이란  
소스 파일에서 첫 번째 문장에 있는 문자열이다. 아마 문서화를 하지 않아본 이들은  
소스코드 첫 문장이 import 문으로 시작하는 경우가 많을텐데 이제는 첫 문장을 docstring으로  
시작하도록 하자. 모듈.\_\_doc\_\_로 모듈의 docs를 읽을 수 있다.  

첫 문장은 모듈의 목적을 기술하는 한 문장으로 구성하며 그 이후의 문단은 사용자가 알아야 하는  
모듈의 동작을 자세히 기술한다. 또한 모듈 내의 중요한 클래스나 함수를 강조한다.

```python
# use_docstring_man.py
#!/usr/bin/env python3

"""Library for testing words for various linguistic patterns.

Testing how words relate to each other can be tricky sometimes!
This module provides easy ways to determine when words you've
found have several special properties.

Available functions:
- palindrome: Determine ife a word is a palindrome.
- check_anagram: Determine if two words are anagrams.
"""

import something...
```

<br>
<br>

### 2.4. 패키지 문서화
모듈과 마찬가지로 패키지의 목적을 기술하는 문장으로 시작하며  
이후 문단은 중요한 서브 패키지나 모듈 등을 기술한다.  

참고로 패키지 docstring은 패키지 디렉토리의 \_\_init.py\_\_에 작성한다.

<br><br>


## 3. 마무리
docstring은 협업하는 개발자가 되고 싶다면 가급적 따르는 것이 좋다.  
하지만 명심해야 할 것은 앞서 설명한 내용들은 convention이며 명령이나 강제는 아니다.  
이 중에서 한 가지를 어겼다고 '잘못 됐다'라고 섣불리 말할 수는 없다는 뜻.

<br>
<br>

**핵심정리**
* 모든 모듈, 클래스, 함수를 docstring으로 문서화하자. 코드 업데이트 마다 관련 문서도 업데이트 하자.
* 모듈: 모든 사용자가 알아둬야 할 모듈의 내용과 중요한 클래스와 함수를 설명한다.
* 클래스: class문 다음의 docstring에서 클래스의 동작, 중요한 속성, 서브클래스의 동작을 설명한다.
* 함수와 메서드: def 문 다음의 docstring에서 모든 인수, 반환 값, 일어나는 예외, 동작을 문서화한다.
