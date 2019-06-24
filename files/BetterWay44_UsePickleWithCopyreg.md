## Better Way 44. copyreg로 pickle을 신뢰할 수 있게 만들자

#### 223쪽

* Created : 2019/06/24
* Modified: 2019/06/24

<br>

## 1. pickle 내장 모듈

**[pickle](https://docs.python.org/3/library/pickle.html)은 파이썬에서 제공하는 데이터 직렬화용 내장 모듈 중 하나로, 파이썬 객체를 바이트 스트림으로 직렬화하거나(피클링), 바이트를 객체로 역직렬화(언피클링)하는 데 사용한다.** pickle은 바이트 직렬화용 간단한 내부 라이브러리이기 때문에 pickle로 만든 바이트 스트림을 신뢰할 수 없는 부분과 통신하는 데 사용하면 안 된다. 이는 pickle의 공식문서에서도 강조하고 있는 바이기도 하다.

좀더 추가적인 설명을 하자면 **pickle로 데이터를 직렬화한 포맷은 설계 관점에서 안전하지 못하다.** 직렬화한 데이터에는 데이터 자체뿐 아니라 파이썬 객체를 재구성하는 데 필요한 메타 요소도 담긴다.(직접 실험해보면 직렬화 결과에 데이터만 담기지 않음을 확인할 수 있다.) 이떄 악성 pickle 페이로드로 파이썬 프로그램에서 해당 페이로드를 역직렬화하는 부분을 망가뜨릴 수 있음을 의미한다. 이는 내장 json 모듈이 상대적으로 설계 관점에서 안전한 것과는 대조적이다.

<br>

일단 pickle을 사용한 예부터 만들어보자. 예를 들어 게임에서 플레이어의 진행 상태를 파이썬 객체로 표현하려고 한다고 하자. 게임 상태는 플레이어의 레벨과 남은 생명 수를 포함한다.


```python
import pickle

class GameState:
    def __init__(self):
        self.level = 0
        self.lives = 4
```

프로그램은 런타임 시에 객체를 수정할 수 있다.

```python
state = GameState()
state.level += 1 # 플레이어 레벨업!
state.lives -= 1 # 플레이어 생명 감소
```

사용자가 게임을 끝내면 프로그램은 게임의 상태를 파일에 저장해서 나중에 재개할 수 있게 한다. pickle 모듈을 이용하면 이런 작업을 쉽게 할 수 있다. 다음은 GameState 객체를 파일에 직접 덤프(직렬화, 피클링)하는 코드다.

```python
path = '/tmp/game_states.bin' # 바이트 데이터라 확장자가 '.bin'
with open(path, 'wb') as f: # 파일 메소드에 'b'가 들어감
    pickle.dump(state, f)
```

나중에 파일을 로드하고 직렬화한 적이 없는 것처럼 GameState 객체를 복원한다.

```python
{'level': 1, 'lives': 3}
```

<br>

## 2. pickle 사용 시의 문제점


앞서 pickle의 기본적인 사용법을 확인했다. 사실 사용방법은 json과 같은 문자열 직렬화 모듈 사용법과 거의 동일했다. 저 일반적인 사용법의 문제점은 시간이 지남에 따라 게임의 기능을 확장하면서 발생한다. 플레이어가 포인트를 쌓아가게 하고 싶다고 해보자. 플레이어의 포인트를 추적하려고 GameState 클래스에 새로운 필드를 추가한다.

```python
class GameState:
    def __init__(self):
        self.level = 0
        self.lives = 4
        self.points = 0 # 새 필드 추가
```

pickle로 업데이트된 GameState 클래스의 새로운 객체를 직렬화하는 기능은 이전과 동일하게 동작한다. 다음은 dumps를 사용해 객체를 문자열로 직렬화하고 loads를 사용해 객체로 되돌려서 파일을 이용한 과정을 시뮬레이트하는 코드다.

```python
state = GameState()
pickled = pickle.dumps(state)
unpickled = pickle.loads(pickled)
print(unpickled.__dict__)

{'level': 0, 'lives': 4, 'points': 0}
# 문제없이 동작한다.
```

하지만 **사용자가 오래 전에 저장한 GameState 객체를 이용해서 게임을 재개하면 어떻게 될까?** 다음 코드에서는 새로 정의한 GameState 클래스로 오래된 게임 파일을 언피클한다.

```python
# path는 아까 사용했던 경로
with open(path, 'rb') as f:
    data = pickle.load(f)

print(data.__dict__)

{'level': 1, 'lives': 3}
```

로드 결과, 전에 추가한 'points' 필드가 빠져 있다. 이는 복원된 객체가 GameState 클래스의 정상적인 인스턴스이기 때문에 더 당황스럽다.

```python
assert isinstance(data, GameState) # 문제 없음.
```

이런 동작은 pickle 모듈이 동작할 때 생기는 부작용이다. **pickle을 사용하는 주 용도는 객체를 쉽게 직렬화하는 것이다. pickle을 단순한 용도 이상으로 사용하자마자 모듈의 기능이 놀랍도록 망가진다.**

<br>

## 3. 해결책: copyreg 내장 모듈 사용하기

이에 대한 해결책으로 내장 모듈 [copyreg](https://docs.python.org/3/library/copyreg.html)을 사용할 것이다. **이 모듈의 이름은 'copy register'의 약자로서 특정 객체를 피클링할 때 사용할 함수를 제공하는 방법을 제공하는 유틸리티 모듈이다.** pickle과 copy 모듈은 이런 객체를 피클링하거나 복사(copying)할 때 이 모듈을 사용하면 좋다. **모듈은 객체 생성자에 클래스가 아닌 설정 정보를 제공한다. 이때 이런 생성자는 팩토리 함수일 수도 있고 클래스 객체일 수도 있다.**

copyreg을 사용해서 앞선 장의 문제를 해결해보자. **GameState 객체가 언피클링 후에 항상 모든 속성을 담음을 보장하는 가장 간단한 방법은 기본 인수가 있는 생성자를 사용하는 것이다.** 다음은 이 방법으로 재정의한 생성자다.


```python
STATE_DEFAULTS = {
    'level': 0,
    'lives': 4,
    'points': 0,
}

class GameState:
    def __init__(self, **kwargs):
        if not kwargs:
            kwargs = STATE_DEFAULTS

        for key, value in kwargs.items():
            setattr(self, key, value)

        for key, value in STATE_DEFAULTS.items():
            if key not in kwargs:
                setattr(self, key, value)
```

이제 본격적으로 copyreg을 사용해보자. copyreg은 사용법이 있으며 이 과정을 일단은 그대로 따라가면 된다.

이 생성자를 피클링용(직렬화용)으로 사용하려고 GameState 객체를 받아 copyreg 모듈용 파라미터 튜플로 변환하는 헬퍼 함수를 정의한다. 반환된 튜플은 언피클링에 사용할 함수와 이 함수에 전달할 파라미터를 담는다.

```python
def pickle_game_state(game_state):
    kwargs = game_state.__dict__
    return unpickle_game_state, (kwargs,)
```

이제 *unpickle\_game\_state* 헬퍼를 정의해야 한다. 이 함수는 직렬화된 데이터와 *pickle\_game\_state* 로부터 가져온 파라미터를 받고 그에 해당하는 GameState 객체를 반환한다. 이 함수는 일단은 GameState 생성자를 감싼 아주 작은 wrapper이다.

```python
def unpickle_game_state(kwargs):
    return GameState(**kwargs)
```

일단은 역직렬화 헬퍼 함수는 GameState의 생성자로 인스턴스를 만드는 함수 그 자체로 반환됐다. 향후 프로그램이 더 커지면 보다 복잡하고 추가적인 작업을 추가할 수도 있겠다.

마지막으로 **내장 모듈 copyreg으로 GameState 객체와 직렬화 함수를 등록한다.**

```python
import copyreg

copyreg.pickle(GameState, pickle_game_state)
```

일단 직렬화와 역직렬화는 이전과 동일하게 동작한다.

```python
state = GameState()
state.points += 1000
data = pickle.dumps(state)
state_back = pickle.loads(data)
print(state_back.__dict__)

{'level': 0, 'lives': 4, 'points': 1000}
```

테스트를 위해 등록을 마치고 나면 GameState의 정의를 다시 변경해서 플레이어에게 사용할 마법의 개수를 부여하게 만든다고 하자. 이 변경은 GameState에 points 필드를 추가할 때와 비슷하다.

```pyton
STATE_DEFAULTS = {
    'level': 0,
    'lives': 4,
    'points': 0,
    'magic': 5, # 필드가 추가됨
}

class GameState:
    def __init__(self, **kwargs):
        if not kwargs:
            kwargs = STATE_DEFAULTS

        for key, value in kwargs.items():
            setattr(self, key, value)

        for key, value in STATE_DEFAULTS.items():
            if key not in kwargs:
                setattr(self, key, value)
```

이번에는 이전과 달리 오래된 객체를 역직렬화해도 빠진 속성 없이 올바른 게임 데이터를 만들어낸다. 그 이유는 *unpickle\_game\_state* 가 GameState 생성자를 직접 호출하기 때문이다. 생성자의 키워드 인자는 파라미터가 빠지면 기본값을 가진다. 따라서 이전 게임 상태 파일이 역직렬화될 때 새로 추가한 _magic_ 필드는 기본값을 받는다.

```python
old_data_back = pickle.loads(data)
print(old_data_back.__dict__)

{'level': 0, 'lives': 4, 'points': 1000, 'magic': 5}
```

전에 _magic_ 값이 없던 상태값이었음에도 언피클링 결과 해당 필드가 추가됐음을 확인할 수 있다.


<br>

## 4. 추가 예제 1: 클래스 버전 관리

이번에는 copyreg을 사용한 추가 예제를 만들어보자. 예를 들어 **필드를 추가하는 것이 아닌, 필드를 제거하여 파이썬 객체가 하위호환성을 유지하지 않게 해야할 때도 있다. 이 경우 기본 인수를 사용한 직렬화는 동작하지 않는다.**

게임이 버전업에 버금갈 정도로 업데이트가 되면서 유저에게 절망감을 제공할 수 있는 '생명'의 개념이 좋지 않다고 깨닫고 이 필드를 없애고 싶다고 하자. 다음과 같이 *STATE\_DEFAULTS* 에서 'lives' 필드를 제거한 뒤 GameState를 재선언한다.

```python
STATE_DEFAULTS = {
    'level': 0,
    # 'lives': 4, 
    # 필드를 제거함.
    'points': 0,
    'magic': 5,
}

class GameState:
    def __init__(self, **kwargs):
        if not kwargs:
            kwargs = STATE_DEFAULTS

        for key, value in kwargs.items():
            setattr(self, key, value)

        for key, value in STATE_DEFAULTS.items():
            if key not in kwargs:
                setattr(self, key, value)
```

문제는 이런 코드가 이전 게임 데이터의 역직렬화를 깨뜨린다는 점이다. **이전 데이터에 있던 모든 필드는 그중 하나가 클래스에서 삭제되어도 *unpickle\_game\_state* 함수에 의해 클래스 생성자로 넘겨진다.**


```python
# 필드를 삭제하고 클래스 재정의한 뒤 실행
print(pickle.loads(data).__dict__)

{'level': 0, 'lives': 4, 'magic': 5, 'points': 1000}
```

_lives_ 필드를 삭제했음에도 언피클링 후 _lives_ 필드가 버젓이 객체 상태로 자리잡고 있다. 매우 화나는 일이 아닐 수 없다.

이에 대한 해결책은 **copyreg에 제공하는 함수에 버전 파라미터를 추가하는 것이다.** 새로운 GameState 객체에 pickle을 적용할 때도 새로 직렬화된 데이터는 버전 2로 설정된다.

```python
def pickle_game_state(game_state):
    kwargs = game_state.__dict__
    kwargs['version'] = 2
    return unpickle_game_state, (kwargs,)
```

피클링 헬퍼 함수를 업데이트해서 새로운 객체에는 버전 정보를 추가하게 했다. 따라서 이전 객체에는 이 _version_ 필드가 없을 것이다.

이제 **언피클 헬퍼 함수에 버전 정보가 없으면 오래된 데이터이기 때문에, 여기서 _lives_ 필드를 제거한다.**

```python
def unpickle_game_state(kwargs):
    version = kwargs.pop('version', 1)
    if version == 1:
        kwargs.pop('lives')
    return GameState(**kwargs)
```

이제 이전 객체를 역직렬화하는 기능이 올바르게 동작한다.

```python
print(pickle.loads(data).__dict__)

{'level': 0, 'magic': 5, 'points': 1000}
# lives 필드가 삭제됨
```

<br>

## 5. 핵심 정리

* 내장 모듈 pickle은 신뢰할 수 있는 프로그램 간에 객체를 직렬화하고 역직렬화하는 용도로만 사용할 수 있다.
* pickle 모듈은 간단한 사용 사례를 벗어나는 용도로 사용하면 제대로 동작하지 않을 수 있다.
* 빠드린 속성 값을 추가하거나 클래스에 버전 관리 기능 등을 제공하려면 pickle과 내장 모듈 copyreg을 같이 사용하자.
