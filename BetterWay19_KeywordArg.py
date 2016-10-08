# 75쪽. 키워드 인수로 선택적인 동작을 제공하자.
# 2016/10/08 작성.

#######################################################################################

############ part 1.
# 파이썬에서 위치(positional) 인수로 함수를 호출하는 것은 일반적인 방법이다.

def remainder(number, divisor):
	"""주어진 수의 나머지를 구한다.
	"""
	return number % divisor

assert remainder(20, 7) == 6

"""
기본적으로 파이썬 함수의 위치 인수를 모두 키워드 인수로 전달할 수도 있다.
이때 인수의 이름을 함수 호출의 괄호 안에 있는 할당문에서 사용한다.
필요한 위치 인수를 모두 지정한다면 키워드 인수로도 전달 가능.
그리고 위치 인수와 키워드 인수를 섞어서 사용할 수도 있다.
"""

assert remainder(20, 7) == remainder(20, divisor = 7) == remainder(divisor=7, number=20)
# 모두 동일하다! 그리고 키워드 인수로 쓰면 순서를 신경쓰지 않아도 된다.

# 그러나 위치 인수는 키워드 인수 앞에 지정해야 한다. 

# remainder(number=20, 7,)
#>>> SyntaxError: positional argument follows keyword argument


""" 키워드 인수의 유연성은 세 가지 중요한 이점이 있다.
1. 코드를 처음 보는 사람이 함수 호출을 더 명확히 이해할 수 있다.
- remainder(20, 7)만 봐서는 함수가 무슨 역할을 하는지 유추하기 더 힘들 것이다.
2. 함수를 정의할 때 기본값을 설정할 수 있는 것이다.
- 덕분에 함수에서 대부분은 기본값을 사용하지만 필요할 때 부가 기능을 제공할 수 있다.
"""

"""
예를 들어, 큰 통에 들어가는 액체의 유속을 계산하고 싶다고 해보자.
큰 통의 무게를 잴 수 있다면,  ''' (원래 무게 - 현재 무게) / 경과한 시간 '''
을 계산해서 유속을 계산할 수 있다.
"""

def flow_rate(weight_diff, time_diff):
	return weight_diff / time_diff

weight_diff = 0.5
time_diff = 3
flow = flow_rate(weight_diff, time_diff)
# print("{:.3f} kg per second".format(flow))
#>>> 0.167 kg per second



# 보통은 초당 유속을 계산하는 게 좋다. 그러나 때로는 센서 등의 기본 시간 단위로 측정하는 것이 좋을 때도 있다.
def flow_rate_period(weight_diff, time_diff, time_period=1):
	return weight_diff / time_diff * time_period

# 다음과 같이 함수를 만들면 기본은 1초 단위로 계산하되, 원할 때만 다른 시간 단위를 사용할 수 있다.
# time_period는 선택적 인수가 되었다.


"""
그리고 세 번째 이점은 기존의 호출 코드와 호환성을 유지하면서도 함수의 파라미터를 확장할 수 있는
강력한 이점이라는 것이다.

예를 들어, 킬로그램 단위는 물론 다른 무게 단위로도 유속을 계산하려고 flow_rate_period를 확장한다고 해보자.
원하는 측정 단위의 변환 비율을 새 선택 파라미터로 추가하여 확장한다.
"""

def flow_rate_period(weight_diff, time_diff,
					 time_period=1, units_per_kg=1):
	return weight_diff / time_diff * time_period / units_per_kg

# 이렇게 하면 무게 단위 기본은 1kg가 되지만 원하면 톤(ton) 등의 단위로 바꿔줄 수 있다.




""" 핵심정리
1. 함수의 인수를 위치 인수나 키워드 인수 방식으로 지정할 수 있다.
2. 위치 인수만으로는 호출코드를 이해하기 어려울 때 키워드 인수를 쓰면 인수의 목적이 명확해진다.
3. 키워드 인수에 기본값을 지정하면 함수에 새 동작을 쉽게 추가할 수 있다. 
특히 함수를 호출하는 기존 코드가 있을 때 사용하면 좋다.
4. 선택적인 키워드 인수는 항상 위치가 아닌 키워드로 넘겨야 한다.(가독성을 위해)
"""
