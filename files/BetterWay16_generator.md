## Better Way 16. 리스트를 반환하는 대신 제너레이터를 고려하자

#### 63쪽

* Created : 2017/02/04
* Modified: 2019/05/11

<br>

## 1. generator

단어들의 index를 저장하는 리스트를 만드는 함수를 만들자.


```python
def index_words(text):
    result = []
    if text:
        result.append(0)
    for index, word in enumerate(text):
        if word == ' ':
            result.append(index + 1)
    return result


print(index_words('I have a dream that one day, my children go to heaven.'))
```

같은 함수를 제너레이터를 사용해 다시 만든다.

```python
def index_words_iter(text):
    if text:
        yield 0
    for index, letter in enumerate(text):
        if letter == ' ':
            yield index + 1

result = list(index_words_iter('okay! Joe, come on!'))
print(result)
```

파일에서 입력을 한 번에 한 줄씩 읽어서 해보자.

```python
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
```
