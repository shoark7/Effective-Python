

# 72쪽. 가변 위치 인수로 깔끔하게 보이게 하자.
# 2016/09/03일 작성.

#######################################################################################

# 선택적인 위치 인수( *args로 많이 알려져 있다. )를 받게 만들면 함수 호출을 더 명확하게 할 수 있고
# 보기에 방해가 되는 요소를 없앨 수 있다.


# 예를 들어 디버그 정보 몇 개를 로그로 남긴다고 할 때, 이누의 개수가 고정되어 있다면
# 메시지와 값 리스트를 받는 함수가 필요할 것이다.

# def log(message, values):
#         if not values:
#             print(message)
#         else:
#             values_string = ', '.join(str(x) for x in values)
#             # ↑ help(str.join)을 검색해본 결과 인자가 iterable... 그래서 리스트 컴프리핸션이 가능하다.
#             print('%s: %s' % (message, values_string))

# log('my numbers are', [1,2])
# log('hi, there', [])

# 위 함수의 문제점은 로그로 남길 값이 없을 때 빈 리스트를 넘겨야 한다는 점.. 불편한 일이다.
# 이때 *args 를 사용하는 것이다.


def log(message, *values):
        if not values:
            print(values) # 어떤 values 값이 들어갔는지 확인해보기 위해 임시적으로 넣었던 코드
            print(message)
        else:
            print(values)
            values_str = ', '.join(str(x) for x in values)
            print('%s: %s' % (message, values_str))


# log('my numbers are', 1, 2, 3)
# log('hi, there')

# favorites = [7, 33, 99]
# log('Favorites', *favorites, 1, 2, 3)

"""
다음과 같이 *args를 사용하면 필수적으로 값을 대입해야 하는 변수 외에 값이 없거나, 값의 개수가 가변적일 때
유동적으로 개수를 조절할 수 있다. 이 가변적 값들은 함수 안에 "튜플"로 전달된다. 바로 위의 코드를 보면
*values 인자에 리스트와 여러 숫자를 같이 넣었는데 "*favorites라고 하면 값들을 모두 풀어헤친 다음에 6개의 값을
갖는 튜플"을 반환했음을 알 수 있다.
"""



"""
위와 같은 방법에는 문제가 있었으니...
1. 가변 인수가 함수에 전달되기에 앞서 항상 튜플로 변환된다.
  함수를 호출하는 쪽에서 이터레이터에 '*'를 사용하면 제너레이터가 모두 소진될 때까지
  순회된다. 따라서 결과로 만들어지는 튜플은 메모리를 너무 잡아 먹어 프로그램이 죽을 수 있다.
        ↓↓↓↓↓
"""
def my_generator():
        for i in range(10):
            yield i

def my_func(*args):
    type(args)


it = my_generator()
my_func(*it)

"""
위를 보자. def my_func에서 *args는 여러 개의 가변 인수를 받는다는 의미이다.
그리고 마지막 줄의 my_func는 it라는 이터레이터를 튜플로 변환한 뒤 그 모든 값을 인자로 집어넣는다는 의미가 된다.
*args를 받는 함수는 인수 리스트에 있는 입력의 수가 적당히 적다는 사실을 아는 상황에서 좋은 방법.
이런 함수는 많은 리터럴이나 변수를 한꺼번에 넘기는 함수 호출에 이상적이다.
"""


"""
두 번째 문제점은
2. 추후에 호출 코드를 모두 변경하지 않고서는 새 위치 인수를 추가할 수 없다는 점
예를 들어 인수 리스트의 앞쪽에 위치 인수를 추가하면 기존의 호출코드가 수정 없이는 이상하게 동작한다.
"""

def log(sequence, message, *values):
    if not values:
        print('{} : {}'.format(sequence, values))
    else:
        values_str = ', '.join(str(x) for x in values)
        print('{}: {}: {}'.format(sequence, message, values_str))

log(1, 'favorites', 7,33)
log('Favorite', 7, 33)

# 위 코드의 문제점은 두 번째 호출이 sequence 인수를 받지 못했기 때문에
# 7을 message로 사용한다는 점. 이런 버그는 코드에서 예외를 일으키지 않기 때문에
# 발견하기 매우 어렵다. 이것을 없애려면 *args를 받는 함수를 확장할 때 키워드 전용 인수를 사용해야 한다.
# 추후에 배운다.

# 이것을 풀어서 설명하면 이전 log 함수를 사용한 수많은 예가 있는데,
# 함수를 조금 변형하면서 그 점이 log 함수의 활용들에서 오류를 일으키지 않고 정상적으로 출력되는 것.
# 위와 같이 이전 로그 함수 호출식을 일일이 다 변경해줘야 한다는 것이다.

