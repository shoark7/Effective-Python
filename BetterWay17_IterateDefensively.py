import os

# 66쪽. 인수를 순회할 때는 방어적으로 하자.
# 2016/09/02일 작성.

#####################################################################################################
# 어떤 상황에서 리스트, 제너레이터를 써야 할까? 제너레이터의 한계나 문제점은 없을까? 알아보자.
# 가정상황은 한 시의 도시들의 인구수를 담은 데이터 파일이 있고 그것을 로드해서 정규화한다고 생각하자.


# 그 파일이 있는 디렉토리로 이동한다. 이 설정은 내 노트북의 설정이며 사람마다 물론 다를 것이다.
os.chdir(r'c:\Users\Stonehead Park\Desktop')


# 도시별로 정규화를 하는 정규화 함수를 만든다.
def normalize(numbers):
    total = sum(numbers)
    result = []
    for value in numbers:
        percent = 100 * value / total
        result.append(percent)
    return result


# 파일에서 도시의 인구를 읽어들이는 함수도 정의한다
def read_population(data_path):
    with open(data_path) as fp:
        for line in fp:
            yield int(line)
#
#
#
# # it = read_population('example.txt')
# # percentages = normalize(it)
# # print(percentages)
#
#

"""
다음의 결과는 놀랍게도 [] 빈 리스트이다. 왜 그럴까? 이유는 이터레이터의 특성과 관련 있다.
이터레이터는 한 번 순회하면 그 다음부터는 StopIteration 예외를 일으킨다.
그러니까 더 이상 사용할 수 없다. 위의 normalize 함수에서 문제가 발생했다.
그 원인은 바로 sum(numbers)에서 한 번 소진하고, for value in numbers에서 한 번 더 호출해서
그런 것이다. 이 때는 방어적으로 numbers를 리스트로 복사해서 사용하면 문제가 없다.
"""



# normalize를 변형한 normalize_copy 함수를 정의한다.
def normalize_copy(numbers):
    numbers = list(numbers) # 위와 같이 리스트로 확정지어서 재사용이 가능하도록 한다
                            # 명심하자. 정의는 우리가 하지만 어떤 클래스가 들어올지는 우리가 알 수 없다.
    total = sum(numbers)
    result = []
    for value in numbers:
        percent = 100 * value / total
        result.append(percent)
    return result

# 결과물을 확인하자.
# it = read_population('example.txt')
# percentages = normalize_copy(it)
# print(percentages)



"""
결과는 제대로 나온다. 이 방법의 문제점은
복사한 복사본의 용량이 클 수도 있다는 것. 이런 이터레이터를 복사하면
한순간에 프로그램의 메모리가 고갈되어 동작을 멈출 수도 있다.
이 문제를 피하는 한 가지 방법은 호출될 때마다 새 이터레이터를 반환하는 함수를 받게 만드는 것.
                                    ↓↓↓↓
"""

def normalize_func(get_iter):
    total = sum(get_iter())
    result = []
    for value in get_iter():
        percent = 100 * value / total
        result.append(percent)
    return result

percentages = normalize_func(lambda: read_population('example.txt'))
print(percentages)

"""
위 방식은 잘 작동하지만 세련되어 보이지는 않는다. 같은 결과를 얻는 더 좋은 방법은
이터레이터 프로토콜을 구현한 새 컨테이너 클래스를 제공하는 것.

Iterator protocol : for 루프와 관련 표현식이 컨테이너 타입의 콘텐츠를 탐색하는 방법을 말한다.
for x in foo와 같은 문장을 파이썬이 받아들일 때 실제로는 iter(foo)를 호출한다.
__iter__ 메서드는 (__next__라는 특별한 메서드를 구현하는) 이터레이터 객체를 반환해야 한다.
마지막으로 for 루프는 이터레이터를 모두 소진할 때까지 이터레이터 객체에 내장 함수 next를 계속 호출한다.
                            ↓↓↓↓↓
"""

class ReadPopulation(object):
    def __init__(self, data_path):
        self.data_path = data_path

    def __iter__(self):
        with open(self.data_path) as fp:
            for line in fp:
                try:
                    yield int(line)
                except:
                    pass


visits = ReadPopulation('example.txt')
percentages = normalize(visits)
print(percentages)

"""
ReadPopulation 컨테이터 클래스를 구현했다. __iter__ 라는 메소드를 정의했다.
이렇게 만들면 normalize에서 이터레이터를 두 번 호출하지만 각각 다르게 호출되어서
StopIteration을 만나지 않는다.

* help(sum)을 확인해보면 sum의 인자는 iterable이다. 그러니까 sum에는 단순히 1,2,3 와 같은 식으로
 인자를 넣으면 계산이 되지 않으며 ReadPopulation의 객체를 sum에 넣으면 __iter__ 함수가 내부적으로
 실행이 되는 것이다. 이렇게 생각해보면 sum의 내부 계산방식은 인자를 하나씩 읽어서 더한 결과를 내놓는 방식이라고
 유추해볼 수 있다.
"""

def normalize_defensive(numbers):
    if iter(numbers) is iter(numbers):
        raise TypeError('Must supply a container')
    total = sum(numbers)
    result = []
    for value in numbers:
        percent = 100 * value / total
        result.append(value)
    return result


"""
  위의 보수적 정규화 함수는 무슨 뜻일까? 처음보면 iter(numbers) is iter(numbers)가 당연히
궁금할 것이다. 여기서 공부할 대목이 다가온다.
  help(iter)를 쳐보자. iterator를 만드는 내장 함수이다. iter 함수의 인자로 iterator를 넘기면
  iterator 자체가 나온다. 왜 그런가 하면, iterator는 내용물을 한 번 순회하면 더는 사용할 수 없는
  (정확히는 StopIteraton 오류만 출력되는) '일회용' 객체이다. 그래서 iter( iterator )하면
  본연의 자체가 나오지 다른 것을 출력할 이유가 없다. 그러가 이터레이터 컨테이너 클래스에서는
  iter()함수가 적용될 때마다 새로운 iterator 객체가 생성되어서 연산을 실행한다. 아까 normalize에서
  ReadPopulation이 문제없이 실행된 것을 보면 알 수 있다. 따라서 iter(iterator)를 사용할 때마다
  서로 다른 객체가 생성되는 것이고 , iter(numbers) is iter(numbers)가 False가 나오게 된다.
  일반 이터레이터를 쓰면 True가 나올 것이다. 이렇게 함수를 만듦으로써 단순 이터레이터가 입력되는 것을
  막을 수 있다.

    즉 결론을 내리면 만약 함수에서 양이 리스트로 처리하기에 많고, 또한 이터레이터를 두 번 이상 사용해야 한다면
    위와 같이 이터레이커 컨테이너 클래스를 활용해서 써도 괜찮을 것 같다. __iter__의 활용법을 알게 된 것 같다.
"""
