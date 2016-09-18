from urllib.parse import parse_qs
# urllib.parse는 python 3의 모듈이다. 2의 경우엔 urlparse 모듈을 사용하자.


# 24쪽. 복잡한 표현식 대신 헬퍼 함수를 작성하자
# 2016/09/18일 작성.

"""
파이썬의 간결한 문법을 사용하면 많은 로직을 표현식 한 줄로 쉽게 작성할 수 있다.
예를 들어, URL에서 쿼리 문자열을 디코드해야 한다고 생각해보자. 다음 예에서 각 쿼리 문자열 파라미터는 정수 값이다.
"""

my_values = parse_qs('red=5&blue=0&green=',keep_blank_values=True)
# print(repr(my_values))


"""
parse_qs()의 인자에 따라 값이 여러 개 존재할 수도 있고, 한 개만 있을 수도 있으며, 값이 비어있을 수도 있다.
만약 딕셔너리에 get 메서드를 사용ㅎ아면 각 상황에 따라 다른 값을 반환할 것이다.

"""

# print('Red     ',my_values.get('red'))
# print('Green   ',my_values.get('green'))
# print('Opacity ',my_values.get('opacity'))

"""
my_values라는 딕셔너리에는 Opacity라는 키가 없다. get메소드는 없는 값을 요구받았을 때 None을 반환한다.
green 처럼 값이 비어 있거나, opacity처럼 None이 반환된다면 기본적으로 0이 할당된다면 좋을 것이다.
이 작업을 불(bool)로 처리할 수도 있다.

파이썬의 문법 덕분에 불 표현식으로도 아주 쉽게 처리할 수 있다. 이때 사용하는 트릭은
파이썬에서는 빈 문자열, 빈 리스트, 0이 모두 False로 처리된다는 점이다.
따라서 다음 표현식들의 결과는 첫 번째 서브 표현식이 False일 때 'or' 연산자 뒤에 오는 서브 표현식을 평가한 값이 된다.
"""
red = my_values.get('red', [''])[0] or 0
green = my_values.get('green', [''])[0] or 0
opacity = my_values.get('opacity', [''])[0] or 0

# print('Red     :     %r' % red)
# print('Green   :     %r' % green)
# print('Opacity :     %r' % opacity)

"""  코드 결과
Result ↓↓↓
Red     :     '5'
Green   :     0
Opacity :     0
"""


""" 해설
red의 경우는 키가 my_values 안에 있다. 값은 '5'만 있는 리스트이다. 암시적으로 True가 되므로
red는 or 표현식의 첫 번째 부분을 할당 받는다.

green의 경우는 키는 있으나 값이 존재하지 않는다. 빈 문자열은 암시적으로 False이므로 or 표현식의 결과는 0이 된다.

opacity의 경우 키 자체가 존재하지 않는다. get 메서드는 딕셔너리에 키가 없으면 두 번째 인수를 반환한다.
위의 코드는 green과 opacitiy가 같은 동작을 한다.
"""


""" 위 코드의 문제점
이 표현식은 읽기가 어려울 뿐만 아니라 여전히 필요한 작업을 다 수행하지도 않는다.
위에서 숫자 5는 '5', 즉 문자 5로 표현되었는데 이를 정수화해야 할 것이다.
"""
red = int(my_values.get('red', [''])[0] or 0)

""" 계속
위 코드는 읽기 무척 어렵다. 시각적 방해 요소가 너무 많다. 코드를 처음 보는 사람은
식을 이해하기 위해 각 부분을 떼어내서 이해하느라 시간을 많이 뺏길 것이다.

코드가 한 줄로 짧기는 하지만, 정말 중요한 건 가독성이다.
한 줄에 모두 집어넣는 건 의미가 없다.

"""


""" if / else로 좀 더 쉽게 시각화하기
파이썬 2.5에 추가된 if/else 조건식(삼항 조건식)을 활용하면
코드를 짧게 하면서도 더 명확하게 표현할 수 있다.


"""

red = my_values.get('red',[''])
red = int(red[0]) if red[0] else 0

""" 해설
이 코드가 한 줄 더 늘어나긴 했지만 훨씬 낫다.
덜 복잡한 상황에서는 if/else 조건식을 쓰면 코드를 명확하게 이해할 수 있다.
식을 더 펼쳐 모든 로직을 길게 보면 더 직관적이다.
"""

green = my_values.get('green', [''])
if green[0]:
    green = int(green[0])
else:
    green = 0


""" 헬퍼 함수의 필요성
이 로직을 반복해서 사용해야 한다면 헬퍼 함수를 만드는 게 좋다.
"""

def get_first_int(values, key, default = 0):
    found = values.get(key, [''])
    if found[0]:
        found = int(found[0])
    else:
        found = default
    return found

""" 해설
위의 헬퍼함수를 쓰면 or를 사용한 복잡한 표현식이나 if/else 조건식을 사용한 두 줄짜리 버젼을 쓸 때보다
호출 코드가 더 명확해진다.
"""

green = get_first_int(my_values, 'green')


""" 해설
표현식이 복잡해지기 시작하면 최대한 빨리 해당 표현식을 작은 조각으로 분학하고,
로직을 헬퍼 함수로 옮기는 방안을 고려해야 한다. 무조건 짧은 코드를 만들기보다는
가독성을 선택하는 편이 낫다. 이렇게 이해하기 어려운 복잡한 표현식에는 파이썬의
함축적인 문법을 사용하면 안 된다.

"""



""" 핵심 정리
* 파이썬의 문법을 이용하면 한 줄짜리 표현식을 쉽게 작성할 수 있지만 코드가 복잡해지고 읽기 어려워진다.

* 복잡한 표현식은 헬퍼 함수로 옮기는 게 좋다. 특히, 같은 로직을 반복해서 사용해야 한다면
헬퍼 함수를 사용하자.

* if/else 표현식을 이용하면 or나 and 같은 불 연산자를 사용할 때보다 읽기 수월한 코드를 작성할 수 있다.
"""
