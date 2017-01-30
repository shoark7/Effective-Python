

# 63쪽, 리스트를 반환하는 대신 제너레이터를 고려하자.
import itertools



# 1. 단어들의 index를 저장하는 리스트를 만드는 함수를 만들자.
def index_words(text):
    result = []
    if text:
        result.append(0)
    for index, word in enumerate(text):
        if word == ' ':
            result.append(index + 1)
    return result

# 테스트
# print(index_words('I have a dream that one day, my children go to heaven.'))



# 2. 같은 함수를 제너레이터를 사용해 다시 만든다.

def index_words_iter(text):
    if text:
        yield 0
    for index, letter in enumerate(text):
        if letter == ' ':
            yield index + 1

result = list(index_words_iter('okay! Joe, come on!'))
print(result)



# 3. 파일에서 입력을 한 번에 한 줄씩 읽어서 해보자.

def index_file(handle):
    offset = 0
    for line in handle :
        if line:
            yield offset
        for letter in line:
            offset += 1
            if letter == ' ':
                yield offset

    with open('somebody.txt', 'r') as f:
        it = index_file(f)
        result = itertools.islice(it, 0, 3)
        print(list(result))




