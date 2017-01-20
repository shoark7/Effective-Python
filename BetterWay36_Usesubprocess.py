# 172쪽. 자식 프로세스를 관리하려면 subprocess를 사용하자.
# 2017/01/20 작성

## Part 1. 병행성과 병렬성
"""
병행성(concurrency)이란 컴퓨터가 여러 일을 마치 동시에 하듯이 수행하는 것을 말한다.
예를 들어 CPU 코어가 하나인 컴퓨터에서 운영체제는 단일 프로세서에서 실행하는 프로그램을 빠르게 변경한다.
이 방법으로 프로그램을 교대로 실행하여 프로그램들이 동시에 실행하는 것처럼 보이게 한다.

병렬성(parallelism)은 여러 작업을 동시에 실행하는 것이다.
CPU 코어가 여러 개인 컴퓨터는 여러 프로그램을 동시에 실행할 수 있다.
각 CPU 코어가 각기 다른 프로그램의 명령어를 실행하여 각 프로그램이 같은 순간에 실행하게 해준다.
"""

"""
병렬성과 병행성 사이의 가장 큰 차이점은 속도 향상이다. 
한 프로그램에서 서로 다른 두 실행 경로를 병렬로 진행하면 전체 작업에 걸리는 시간이 절반으로 준다.
즉, 실행 속도가 두 배로 빨라진다.

반면에 병행 프로그램은 수 천 가지 실행 경로를 병렬로 수행하는 것처럼 보이게 해주지만 전체 작업 속도는 향상되지 않는다.

파이썬을 쓰면 병행 프로그램을 쉽게 작성할 수 있다. 시스템 호출, 서브프로세스, C 확장을 이용한 병렬작업에도 파이썬을 쓸 수 있다.
그러나 병행 파이썬 코드를 실제 병렬로 실행하게 만드는 건 정말 어렵다.
이런 미묘한 차이가 생기는 상황에서 파이썬을 최대한 활용하는 방법을 알아야 한다.
"""

## Part 2. subprocess - 1
"""
파이썬은 실전에서 단련된 자식 프로세스 실행과 관리용 라이브러리를 갖추고 있다.
따라서 명령줄 유틸리티 같은 다른 도구들을 연계하는 데 아주 좋은 언어다.(ex. shell)
기존 쉘 스크립트가 시간이 지나면서 점점 복잡해지면, 자연히 파이썬 코드로 재작성하여 가독성과 유지보수성을 확보하려 하기 마련이다.

파이썬으로 시작한 자식 프로세스는 병렬로 실행할 수 있고, 그래서 파이썬을 사용하면 CPU 코어를 모두 이용해
프로그램의 처리량을 극대화할 수 있다.

파이썬에서 서브프로세스(자식 프로세스)를 실행하는 방법은 여러 개 있어 왔는데 요즘 최선의 방법은 
내장 'subprocess' 모듈을 사용하는 것이다.
"""
import os
import subprocess
from time import time

proc = subprocess.Popen(
	['echo', 'Hello from the child!'],
	stdout=subprocess.PIPE)
out, err = proc.communicate()
print(out)  # b'Hello from the child!\n'

# 자세한 내용은 https://docs.python.org/3/library/subprocess.html 에 있는데 다 읽는 것을 추천한다.
# 여기서는 간단한 내용만 다룬다.

"""
위의 코드를 보면
1. subprocess.Popen 
	서브 프로세스를 생성하는 생성자이다. 수많은 인자를 받는다.
2. ['echo', 'Hello from the child!'],
	실행할 명령을 리스트로 입력한다. 의미 있는 단위로 나누어야 한다.
3. stdout=subprocess.PIPE)
	프로세스의 결과물을 표준 출력으로 지정할 수 있는데(stdout) PIPE로 그 값을 내가 원하는 시간대에 가져올 수 있다.
4. proc.communicate()
	이 메소드는 (stdout, stderr)를 튜플로 반환한다.
"""

"""
자식 프로세스는 부모 프로세스와 파이썬 인터프리터와는 독립적으로 실행된다.
자식 프로세스의 상태는 다른 작업을 하는 동안 주시적으로 폴링된다.(polling)
"""

proc = subprocess.Popen(['sleep', '0.3'])
while proc.poll() is None:
    print('Child is working')
print('Exit status', proc.poll())

# >>>
#Child is working
#Child is working
# ...
# Child is working
# Exit status 0

"""
poll 메서드는 자식 프로세스가 종료되지 않았으면 None을 종료하고
끝나면 정수의 리턴코드를 반환한다.

위에서는 0.3 초 동안 프로세스가 실행되었고 그 동안 무수한 'Child is working'이 출력되었다.
"""



### Part 3. subprocess - 2
"""
부모에서 자식 프로세스를 떼어낸다는 건 부모 프로세스가 자유롭게 여러 자식 프로세스를 
병렬로 실행할 수 있음을 의미한다.
자식 프로세스를 떼어내려면 모든 자식 프로세스를 먼저 시작하면 된다.
"""

def run_sleep(period):
    proc = subprocess.Popen(['sleep', str(period)])
    return proc
	
start = time()
procs = []

for _ in range(10):
    proc = run_sleep(0.1)
    procs.append(proc)
    
# 이후에는 communicate 메소드로 자식 프로세스들이 I/O를 마치고 종료하기를 기다리면 된다.
for proc in procs:
    proc.communicate()
end = time()
print('Finished in ', end - start) # Finished in  0.12452840805053711

# 이 프로세스들을 순차적으로 실행했다면 전체 지연 시간은 여기서 측정한 약 0.12초가 아니라 1초였을 것이다.


### Part 4. subprocess - 3
"""
파이썬 프로그램에서 파이프를 이용해 데이터를 서브프로세스로 보낸 다음, 서브프로세스의 결과를 받아올 수 있다.
이 방법을 이용하면 다른 프로그램을 활용하여 작업을 병렬로 수행할 수 있다.

예를 들어 어떤 데이터를 암호화하는 데 openssl 명령줄 도구를 사용하려 한다고 하자. 
명령줄 인수와 I/O 파이프를 사용해 자식 프로세스를 실행하는 건 간단하다.
"""

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
    
"""
proc.stdin, proc.stdout은 하나의 file로 취급되어 write, read, flush 등을 모두 쓸 수 있다.
위 식은 파이프로 어떤 data 인자를 받으면 그 인자를 openssl enc로 암호화하는 프로세스를 반환한다는 것을 의미한다.

예제에서는 파이프로 암호화 함수에 임의의 바이트를 전달하지만 실전에서는 사용자 입력, 파일 핸들, 네트워크 소켓 등을 전달할 것이다.
"""

procs = []

for _ in range(3):
    data = os.urandom(10)
    proc = run_openssl(data)
    procs.append(proc)
    
    out, err = proc.communicate()
    print(out[-10:])
 
# 자식 프로세스는 병렬로 실행되고 입력을 소비한다.
# >>>
# b'eQ\xca"\xc5\x04R(=q'
# b'W\xcfj\xbf\x12"\xe7\xb1lj'
# b"\x87\xfdb\x8c`'{f\x0e\x13"


## Part 5. subprocess - 4
"""
자식 프로세스가 종료되지 않거나 입력 또는 출력 파이프에서 블록될 염려가 있다면 
communicate 메서드에 timeout 파라미터를 넘겨야 한다.
이렇게 하면 자식 프로세스가 일정한 시간 내에 응답하지 않을 때 예외가 일으켜 오동작하는
자식 프로세스를 종료할 기회를 얻는다.
"""

proc = run_sleep(10)
try:
    proc.communicate(timeout=0.1)
except subprocess.TimeoutExpired:
    proc.terminate()
    proc.wait()
    
print('Exit status', proc.poll()) # Exit status -15



## Part 6. subprocess - 5
"""
유닉스의 파이프처럼 한 자식 프로세스의 결과를 다른 프로세스의 입력으로 연결하여
병렬 프로세스의 체인을 생설할 수 있다.

다음은 자식 프로세스를 시작하여 md5 명령줄 도구에서 입력 스트림을 소비하게 하는 함수이다.
"""

def run_md5(input_stdin):
    proc = subprocess.Popen(['md5'],
    			    stdin=input_stdin,
    			    stdout=subprocess.PIPE)
    return proc
    
# 이제 데이터를 암호화하는 openssl 프로세스 집합과 암호화된 결과를 md5로 해시하는 프로세스 집합을 시작할 수 있다.

input_procs = []
hash_procs = []

for _ in range(3):
    data = os.urandom(10)
    proc = run_openssl(data)
    input_procs.append(proc)
    hash_proc = run_md5(proc.stdout)
    hash_procs.append(hash_proc)
    
"""
run_openssl 프로세스의 출력, 즉 stdout을 run_md5의 stdin으로 받음으로써 pipe 가 되었다.
일단 자식 프로세스들이 시작하면 이들 사이의 I/O는 자동으로 일어난다. 
할 일은 모든 작업이 끝나고 최종 결과물이 출력되기를 기다리는 것뿐이다.
"""

for proc in input_procs:
    proc.communicate()
    
for proc in hash_procs:
    out, err = proc.communicate()
    print(out.strip())
    
    
"""핵심정리

* 자식 프로세스를 실행하고 자식 프로세스의 입출력 스트림을 관리하려면 subprocess 모듈을 사용하자.
* 자식 프로세스는 파이썬 인터프리터에서 병렬로 실행되어 CPU 사용을 극대화하게 해준다.
* communicate 메서드에 timeout 파라미터를 사용하여 자식 프로세스들이 교착 상태(dead lock)에 빠지거나 멈추는 상황을 막자.

"""
