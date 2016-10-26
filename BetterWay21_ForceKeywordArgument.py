# 83쪽. 키워드 전용 인수로 명료성을 강요하자.
# 2016/10/27 작성.

#######################################################################################
"""
키워드로 인수를 넘기는 방법은 파이썬 함수의 강력한 기능이다.
키워드 인수의 유연성 덕에 코드의 쓰임새를 명료하게 정의할 수 있다.

예를 들어 어떤 숫자를 다른 숫자로 나눈다고 해보자. 어떤 에러를 발생시키지만 예외를 조심해야 한다.
때로는 무한대값을 반환하거나, 0을 반환하고 싶을 수도 있다.
"""
def save_division(number, divisor, ignore_overflow, ignore_zero_division):
	try:
		return number / divisor
	except OverflowError:
		if ignore_overflow:
			return 0
		else:
			raise
	except ZeroDivisionError:
		if ignore_zero_division:
			return float('inf')
		else:
			raise

# 다음 결과는 값이 너무 overflowerror가 발생해 0이 나오게 된다.
result = save_division(1, 10**500, True, False)
print(result)

# 다음은 분모가 0이 되어 무한대가 나오게 된다.
result = save_division(1,0, False, True)
print(result)

"""
위 식의 문제는 무엇일까? 세네번째 인자를 위치인자로 받으면서 무엇이 True이고 무엇이 False인지 알아보기 힘들다.
이 때문에 찾기 어려운 버그가 발생하기 쉽다. 
이런 코드의 가독성을 높이는 방법 중 하나는 키워드 인수를 사용하는 것이다.

"""




def safe_division_b(number, divisor,
					ignore_overflow=False,
					ignore_zero_division=False):

	try:
		return number / divisor
	except OverflowError:
		if ignore_overflow:
			return 0
		else:
			raise
	except ZeroDivisionError:
		if ignore_zero_division:
			return float('inf')
		else:
			raise

"""
처음 함수와 다른 점은 ignore_overflow 인자와 ignore_zero_division 인자의 기본값을 정해주었다.
이렇게 하면 기본적으로는 항상 예외를 일으키지만 필요한 순간 값을 True로 주어 원하는 결과를 구할 수 있다.

"""

print(safe_division_b(1,10**500, ignore_overflow=True))
print(safe_division_b(1,0, ignore_zero_division=True))



"""
이 식의 문제는 키워드가 인수가 선택적이어서 함수를 호출하는 쪽에 키워드 인수로 의도를 명확히 드러내라고
강요할 방법이 없다는 것이다. 앞서 정의한 safe_division_b 함수를 온전히 위치 인자로 호출하는 것이 가능하다.

이처럼 복잡한 함수를 작성할 때는 호출하는 쪽에서 의도를 명확히 드러내도록 요구하는 것이 낫다.
파이썬 3에서는 키워드 전용 인수(keyword-only argument)로 키워드 인자를 강요할 수 있다.
키워드 전용 인수는 키워드로만 넘길 뿐, 위치로는 절대 넘길 수 없다.
"""

def safe_division_c(number, divisor, *,
					ignore_overflow=False,
					ignore_zero_division=False):
	try:
		return number / divisor
	except OverflowError:
		if ignore_overflow:
			return 0
		else:
			raise
	except ZeroDivisionError:
		if ignore_zero_division:
			return float('inf')
		else:
			raise

# 인자에 '*'를 넣어줌으로써 이후의 인자는 모두 키워드 인자라는 것을 선언한다.
# 이제 키워드 인수가 아닌 위치 인수를 사용하는 함수는 동작하지 않는다.

# print(safe_division_c(1, 10**500, True, False))
# >>> TypeError: safe_division_c() takes 2 positional arguments but 4 were given

print(safe_division_c(1, 0, ignore_zero_division=True))
# 기본값을 그대로 쓰는 건 가능하다.


"""핵심정리
1. 키워드 인수는 함수 호출의 의도를 더 명확하게 해준다.
2. 특히 불 플래그를 여러 개 받는 함수처럼 헷갈리기 쉬운 함수를 호출할 때 키워드 인수를 넘기게 하려면
   키워드 전용 인수를 사용하자.
3. 파이썬 3는 함수의 키워드 전용 인수 문법을 명시적으로 지원한다.
"""


"""