## Better Way 36. 자식 프로세스를 관리하려면 subprocess를 사용하자

#### 172쪽

* Created : 2017/01/20
* Modified: 2019/06/13

<br>


## 1. 병행성과 병렬성

**`병행성`(concurrency)이란 컴퓨터가 여러 일을 마치 동시에 하듯이 수행하는 것을 말한다.** 예를 들어 CPU 코어가 하나인 컴퓨터에서 운영체제는 단일 프로세서에서 실행하는 프로그램을 빠르게 변경한다. 이런 **Time sharing의 한 기법을 Context Switching**이라고 한다. 이 방법으로 프로그램을 교대로 실행하여 프로그램들이 동시에 실행하는 것처럼 보이게 한다.

반면 **`병렬성`(parallelism)은 여러 작업을 동시에 실행하는 것이다.** CPU 코어가 여러 개인 컴퓨터는 여러 프로그램을 동시에 실행할 수 있다. 각 CPU 코어가 각기 다른 프로그램의 명령어를 실행하여 각 프로그램이 같은 순간에 실행하게 해준다. 현대의 어지간한 컴퓨터는 CPU 코어를 여러 개 가지고 있다. 내 5년 된 노트북도 확인해보니 코어가 2개이다.

```shell
$ lscpu

Architecture:          x86_64
CPU op-mode(s):        32-bit, 64-bit
Byte Order:            Little Endian
CPU(s):                2 	 # !!!!!!!!!!!
On-line CPU(s) list:   0,1
Thread(s) per core:    1
# 생략...


# lscpu는 Ubuntu에 설치되어 있으며 다른 운영체제에는 없을 수 있음
```

**병렬성과 병행성 사이의 가장 큰 차이점은 속도 향상**이다. 한 프로그램에서 서로 다른 두 실행 경로를 병렬로 진행하면 전체 작업에 걸리는 시간이 절반으로 준다. 즉, 실행 속도가 두 배로 빨라진다.

반면에 병행 프로그램은 수천 가지 실행 경로를 병렬로 수행하는 것처럼 보이게 해주지만 전체 작업 속도는 향상되지 않는다.

파이썬을 쓰면 병행 프로그램을 쉽게 작성할 수 있다. 시스템 호출, 서브프로세스, C 확장을 이용한 병렬작업에도 파이썬을 쓸 수 있다. 그러나 **병행 파이썬 코드를 실제 병렬로 실행하게 만드는 건 정말 어렵다.**

이런 미묘한 차이가 생기는 상황에서 파이썬을 최대한 활용하는 방법을 알아야 한다.


<br>

## 2. subprocess 소개

파이썬은 실전에서 단련된 자식 프로세스 실행과 관리용 라이브러리를 갖추고 있다. 따라서 명령줄 유틸리티 같은 다른 도구들을 연계하는 데 아주 좋은 언어다.(ex. shell) 기존 쉘 스크립트가 시간이 지나면서 점점 복잡해지면, 자연히 파이썬 코드로 재작성하여 가독성과 유지보수성을 확보하려 하기 마련이다.

**파이썬으로 시작한 자식 프로세스는 병렬로 실행할 수 있고, 그래서 파이썬을 사용하면 CPU 코어를 모두 이용해 프로그램의 처리량을 극대화할 수 있다.** 이전부터 파이썬에서 서브프로세스(자식 프로세스)를 실행하는 방법은 여러 개 있었는데 요즘 최선의 방법은 내장 [subprocess](https://docs.python.org/3/library/subprocess.html) 모듈을 사용하는 것이다.

subprocess로 자식 프로세스를 실행하는 방법은 간단하다. 다음 코드에서는 Popen 생성자가 프로세스를 시작한다. communicate 메소드는 자식 프로세스의 출력을 읽어오고 자식 프로세스가 종료할 때까지 대기한다.

```python
import os
import subprocess
from time import time


proc = subprocess.Popen(
    ['echo', 'Hello from the child process!'], stdout=subprocess.PIPE
)

out, err = proc.communicate()
print(out)


b'Hello from the child process!\n'
```

위의 코드를 조금 해석해보자:

* subprocess.Popen 
  - 서브 프로세스를 생성하는 생성자이다. 문서를 살피면 수많은 인자를 받는다.
* ['echo', 'Hello from the child!'],
  - 실행할 명령을 리스트나 단일 문자열로 입력한다. 의미 있는 단위로 나누어야 한다.
* stdout=subprocess.PIPE
  - **프로세스의 결과물의 방향을 표준출력으로 지정할 수 있는데(stdout) 여기서는 PIPE로 지정한다. 실제 쉘에서의 파이프처럼 출력물을 다른 프로세스의 입력으로 전환하는 등의 작업이 가능해진다.**
* proc.communicate()
  - 자식 프로세스가 끝나기까지 기다리고 출력을 받아온다. (stdout, stderr)를 튜플로 반환한다.


**자식 프로세스는 부모 프로세스와 파이썬 인터프리터와는 독립적으로 실행된다.** 자식 프로세스의 상태는 다른 작업을 하는 동안 주기적으로 폴링된다.(polling)

**Popen.poll()에서 `poll`은 실제 운영체제 용어로 보통 저수준 장비 사이에서 서로의 상태나 사용 여부 등을 기다리는 것을 말한다.** 여기서 자식 프로세스의 상태는 파이썬이 다른 작업을 하는 동안 주기적으로 폴링(polling)된다.(즉, 상태를 확인하게 된다.)


```python
proc = subprocess.Popen(['sleep', '0.3'])
while proc.poll() is None:
    print('Child is working')
print('Exit status', proc.poll())


Child is working
Child is working
# ...
Exit status 0
```

`sleep`은 파이썬 함수가 아닌 쉘 커맨드로 몇 초간 다음 쉘 스크립트 실행을 멈추고 대기하는 함수이다. 예제에서는 이 '기다리는 작업'이 종료되기 전까지 무수한 문장을 출력하고 있다.

**poll 메서드는 자식 프로세스가 종료되지 않았으면 None을 반환하고 종료됐으면 정수의 리턴코드를 반환한다.** 위에서는 0.3 초 동안 프로세스가 실행되었고 그동안 무수한 'Child is working'이 출력된 것을 확인할 수 있다.


<br>

## 3. subprocess의 장점: 병렬성

**부모에서 자식 프로세스를 떼어낸다는 건 부모 프로세스가 자유롭게 여러 자식 프로세스를 병렬로 실행할 수 있음을 의미한다.** 자식 프로세스를 떼어내려면 모든 자식 프로세스를 먼저 시작하면 된다.

```python
def run_sleep(period):
    proc = subprocess.Popen(['sleep', str(period)])
    return proc
	
SIZE = 10
start = time()
procs = []

for _ in range(SIZE):
    proc = run_sleep(0.1)
    procs.append(proc)
    
for proc in procs:
    proc.communicate()

end = time()
print('Finished in ', end - start)


Finished in  0.1650395393371582
```

*run\_sleep* 함수는 _period_ 동안 '잠을 자는' 자식 프로세스를 반환한다. 아직 communicate는 실행하지 않아 실제 작동은 하지 않고 있는 상태다. 그리고 _SIZE_ 개만큼 해당 자식 프로세스를 만들어서 두 번째 for문에서 한 번에 실행한다. 그리고 전체 실행시간을 확인해보니 약 0.17초 정도이다.

이 예제에서 생성한 자식 프로세스의 개수는 10개였기 때문에 **만약 프로그램이 병렬로 실행되지 않았다면 1초가 넘는 시간이 걸렸을 것이다. 하지만 10개의 자식 프로세스가 모두 병렬로 실행될 수 있었기 때문에 시간은 0.2초도 걸리지 않았다.**


<br>

## 4. subprocess 활용: 프로세스의 파이프라이닝(Pipelining)

앞선 예제에서 _subprocess.PIPE_ 를 잠깐 살펴봤다. **쉘에서 파이프라이닝(Pipelining)을 통해 프로세스의 출력을 다른 프로세스의 입력으로 전환할 수 있듯이, 자식 프로세스의 입출력을 다른 프로세스의 입출력을 통해 받는 것이 가능하다.**

예를 들어 어떤 데이터를 암호화하는 데 쉘의 `openssl` 명령줄 도구를 사용하려 한다고 하자. 명령줄 인수와 I/O 파이프를 사용해 자식 프로세스를 실행하는 건 간단하다.

```python
def run_openssl(data):
    env = os.environ.copy()
    env['password'] = b'\xe24U\n\xd0Ql3S\x11'
    proc = subprocess.Popen(
        ['openssl', 'enc', '-des3', '-pass', 'env:password'],
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    proc.stdin.write(data)
    proc.stdin.flush() # 자식 프로세스가 입력을 반드시 받게 함.
    return proc
``` 

위 식은 파이프로 어떤 data 인자를 받으면 그 인자를 openssl enc로 암호화하는 프로세스를 반환한다는 것을 의미한다.

각 코드 부분에 대해 간략히 설명하면 다음과 같다.

* _env_
  - 운영체제의 환경변수의 값을 받아와서 password 변수를 임의의 값으로 바꾼다.
* subprocess.Popen( ... )
  - 바뀐 변수값을 바탕으로 openssl을 사용하는 자식 프로세스를 호출한다.
  - 이때 _stdin_, _stdout_ 인자에 모두 PIPE을 줬다. 이는 프로세스의 입력과 출력을 사용자가 제어하겠다는 의미이다. 이 예제에서는 다른 프로세스의 입출력과 파이프라이닝을 한다.
* proc.stdin.write(data)
  - 표준입력(stdin)을 PIPE로 줬기 때문에 사용자가 프로세스에 입력을 직접 줄 수 있다. _write_ 메소드에 겁먹지 말자. **유닉스에서는 프로세스든, 소켓이든 다 파일이니까.**
* proc.stdin.flush()
  - I/O의 관점에서 입력이 바로 프로세스로 넘어가지 않을 수 있다. 성능문제에 있어서 다음 입력까지 기다렸다가 한 번에 chunk로 데이터를 넘길 수도 있기 때문이다. 지금 우리는 바로 프로세스에 데이터를 넘겨야 하기 때문에 _flush_ 메소드로 자료를 확실히 전달한다.


예제에서는 파이프로 암호화 함수에 임의의 바이트를 전달하지만 실전에서는 사용자 입력, 파일 핸들, 네트워크 소켓 등을 전달할 것이다.


```python
procs = []

for _ in range(3):
    data = os.urandom(10)
    proc = run_openssl(data)
    procs.append(proc)
    
    out, err = proc.communicate()
    print(out[-10:])
 

b'eQ\xca"\xc5\x04R(=q'
b'W\xcfj\xbf\x12"\xe7\xb1lj'
b"\x87\xfdb\x8c`'{f\x0e\x13"
```

os.urandom은 인자로 받은 길의의 랜덤 바이트 값을 출력한다. 이 _data_ 변수를 통해 *run\_openssl* 함수를 실행한다.


<br>

단순히 입력을 외부에서 받는 것뿐 아니라 **유닉스의 파이프처럼 한 자식 프로세스의 결과를 다른 프로세스의 입력으로 연결하여 병렬 프로세스의 체인을 생설할 수 있다.**

다음은 md5 명령줄 도구에서 입력 스트림을 MD5 알고리즘으로 암호화하는 자식 프로세스를 반환하는 함수다.

```python
def run_md5(input_stdin):
    proc = subprocess.Popen(
        ['md5sum'], # 운영체제마다 정확한 프로그램 이름이 다름. 'md5' 등.
        stdin=input_stdin,
        stdout=subprocess.PIPE)
    return proc
```
    
이제 **데이터를 암호화하는 openssl 프로세스 집합과 암호화된 결과를 파이프라이닝해 md5로 다시 해시하는 프로세스 집합을 시작할 수 있다.**

```python
input_procs = []
hash_procs = []

for _ in range(3):
    data = os.urandom(10)
    proc = run_openssl(data)
    input_procs.append(proc)
    hash_proc = run_md5(proc.stdout)
    hash_procs.append(hash_proc)
```

*run\_openssl* 프로세스의 출력, 즉 stdout을 *run\_md5*의 stdin으로 입력함으로써 파이프라이닝이 되었다. 일단 자식 프로세스들이 시작하면 이들 사이의 I/O는 자동으로 일어난다. 할 일은 모든 작업이 끝나고 최종 결과물이 출력되기를 기다리는 것뿐이다.

```python
for proc in input_procs:
    proc.communicate()
    
for proc in hash_procs:
    out, err = proc.communicate()
    print(out.strip())


b'4fe204c19bd577feb58224eee3a06508  -'
b'f0b012242bf4bc3331b23eca8cdb0bda  -'
b'601e667ddbf36825b20245c37cc7dbfd  -'
```

<br>

## 5. 자식 프로세스의 강제 종료

**자식 프로세스가 종료되지 않거나 입력 또는 출력 파이프에서 블록될 염려가 있다면 communicate 메서드에 timeout 파라미터를 넘겨야 한다.** 이렇게 하면 자식 프로세스가 일정한 시간 내에 응답하지 않을 때 예외가 일으켜 오동작하는 자식 프로세스를 종료할 기회를 얻는다.

```python
proc = run_sleep(10)
try:
    proc.communicate(timeout=0.1)
except subprocess.TimeoutExpired:
    proc.terminate()
    proc.wait()
    
print('Exit status', proc.poll()) # Exit status -15
```

<br>

## 6. 핵심정리

* 자식 프로세스를 실행하고 자식 프로세스의 입출력 스트림을 관리하려면 `subprocess` 모듈을 사용하자.
* **자식 프로세스는 파이썬 인터프리터에서 병렬로 실행되어 CPU 사용을 극대화하게 해준다.**
* communicate 메서드에 timeout 파라미터를 사용하여 자식 프로세스들이 교착 상태(dead lock)에 빠지거나 멈추는 상황을 막자.

