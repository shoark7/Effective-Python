# 79쪽. 동적 기본 인수를 지정하려면 None과 docstring을 사용하자.
# 2016/10/08일 작성.

#######################################################################################
import time
import datetime
import json

################## Part 1.

""" 
키워드 인수의 기본값으로 동적 타입을 사용해야 할 때도 있다. 예를 들어,
함수를 호출한 시각을 메시지에 포함한다고 하자. 이렇게 만들 수도 있을 것이다.
"""

def log(message, when = datetime.datetime.now()):
	print("{}, {}".format(when, message))

# log("It's me!")
# time.sleep(0.1)
# log("How are you doing?")

#>>> 2016-10-08 09:25:13.881156, It's me!
#>>> 2016-10-08 09:25:13.881156, How are you doing?

"""
이상한 것을 느꼈는가?
우리는 time.sleep으로 함수 호출에 시간차를 주었다. 그런데 출력된 시간이 동일하다!
왜 그럴까?

근본적인 이유는 파이썬 내부의 모듈 함수 정의는 보통 프로그램이 시작할 때, 그러니까
모듈이 로드될 때 한 번만 평가되며, 한 번 로드되면 기본 인자를 다시 평가하지 않기 때문이다.

그러니까, 'when' 인자는 프로그램 시작할 때 한 번만 사용되었으며, 그 시간이 고정된 것이다!
"""

"""
그러면 원하는 값이 나오려면 어떻게 해야 할까?

"이때는 기본값(when)을 None으로 설정하고 함수 실행 시에 시간을 설정한다.
그리고 docstring을 활용해서 함수 설명을 보충하고 문서화 하는 것이 관례다."

"""

def log_new(message, when=None):
	"""Log a message with a timestamp.

	Args:
		message : Message to print.
		when : datetime of when the message occured.
				Defaults to the present time.
	Output:
		return None. Just print the message and timestamp.
	"""

	when = datetime.datetime.now() if when is None else when
	print('{} {}'.format(when, message))

# log_new('hi!')
# time.sleep(0.1)
# log_new('asdf')

#>>> 2016-10-08 09:33:32.826446 hi!
#>>> 2016-10-08 09:33:32.941965 asdf

# 이제 시간이 정확하게 출력되는 것을 알 수 있다.




################## Part 2. 

"""
기본 인수 값으로 None을 사용하는 방법은 인수가 수정가능할 때(mutable) 특히 중요하다.
예를 들어, JSON 데이터로 인코드된 값을 로드한다고 하자. 그러니까 문자열을 진짜 JSON객체로 만든다는 뜻이다.
데이터 디코딩이 실패하면 기본값으로 빈 딕셔너리를 반환하려 한다.
"""

def json_decode(data, default = {}):
	try:
		return json.loads(data)
	except ValueError:
		return default

# 데이터가 json 형식으로 로드되면 그 결과를 반환할 것이고 값이 맞지 않으면 빈 딕셔너리를 반환할 것이다.
# 이 코드에는 치명적인 문제가 있다. 함께 보시죠!

foo = json_decode('i am not json format')
foo['stuff'] = 5
bar = json_decode('i')
bar['beep'] = 'ok?'

# print('Foo : ', foo)
# print('Bar : ', bar)

#>>> Foo :  {'beep': 'ok?', 'stuff': 5}
#>>> Bar :  {'beep': 'ok?', 'stuff': 5}


"""
위 결과를 주목해주길 바란다.
foo와 bar에 들어간 인자는 모두 json 형식이 아니므로 빈 딕셔너리가 반환될 것이다.
일반적으로 생각할 때, foo, bar는 서로 다른 딕셔너리가 되는 것이 맞다.
그런데 일련의 식을 거친 후, foo, bar를 출력하면 서로가 같아졌음을 알 수 있다.

근본적으로 첫 번째 경우와 동일하다. 기본 인수 값은 모듈이 로드될 때 딱 한번만 평가되므로,
기본값으로 설정한 딕셔너리를 모든 json_decode에서 공유한다. 그래서 이런 문제가 생긴 것. 수정하자.
"""


def json_decode_new(data, default = None):
	"""Load JSON data from a string.

	Args:
		data : JSON data to decode.
		default : value to return if decoding fails.
				Defaults to an empty dictionary.

	Output:
		return a JSON object, but an empty dictionary if decoding fails.
	"""
	if default is None:
		default = {}
	try: 
		return json.loads(data)
	except ValueError:
		return default

foo = json_decode_new('i am not json format')
foo['stuff'] = 5
bar = json_decode_new('i')
bar['beep'] = 'ok?'

print(json_decode_new.__doc__)
# print('Foo : ', foo)
# print('Bar : ', bar)

#>>> Foo :  {'stuff': 5}
#>>> Bar :  {'beep': 'ok?'}

# 원하는 결과가 출력됨을 알 수 있다.

""" 핵심정리
1. 기본 인수는 모듈 로드 시점에 함수 정의 과정에서 딱 한 번만 평가된다.
그래서 ({}나 []와 같은) 동적값에는 이상하게 동작하는 원인이 되기도 한다.
2. 값이 동적인 키워드 인수에는 기본값으로 None을 사용하자. 
그러고 나서 함수의 docstring에 실제 기본 동작을 문서화하자.
"""