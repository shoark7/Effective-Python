## Better Way 59. tracemalloc으로 메모리 사용 현황과 누수를 파악하자

#### 301쪽

* Created : 2019/07/06
* Modified: 2019/07/06

<br>

## 1. 파이썬의 내부 메모리 관리

일반적인 CPython의 기본구현은 `참조 카운팅`(reference counting)으로 메모리를 관리한다. 참조 카운팅은 객체의 참조가 모두 해제되면 참조된 객체 역시 정리됨을 보장한다. 또한 CPython은 자기 참조 객체가 결국 가비지 컬렉션되는 것을 보장하는 사이클 디텍터(cycle detector)도 갖추고 있다.

이론적으로는 대부분의 파이썬 프로그래머가 프로그램에서 일어나는 메모리 할당과 해제를 걱정할 필요가 없다는 의미다. 즉, 언어와 CPython 런타임이 자동으로 처리한다. 그러나 실제로 프로그램은 결국 참조 때문에 메모리 부족에 처한다. 파이썬 프로그램이 어디서 메모리를 사용하거나 누수를 일으키는지 알아내는 건 힘든 도전 과제다.

**메모리 사용을 디버깅하는 첫 번째 방법은 내장 모듈 gc(garbage collection)에 요청하여 가비지 컬렉터에 알려진 모든 객체를 나열하는 것이다.** gc가 그렇게 정확한 도구는 아니지만 이 방법을 이용하면 프로그램의 메모리가 어디서 사용되는지 금방 알 수 있다.  

다음과 같이 gc를 사용해 현재 런타임에 존재하는 모든 객체의 수를 출력하는 프로그램을 만들자. 또 할당된 객체들의 샘플을 소량 출력한다.

```python
import gc

found_objects = gc.get_objects()
print(f'{len(found_objects)} objects now')

58185 objects now



for obj in found_objects[:3]:
    print(repr(obj)[:100])


KeyPress(key=Key('<C-J>'), data='\n')
{'key': Key('<C-J>'), 'data': '\n'}
[_Binding(keys=(Key('<Any>'),), handler=<function self_insert at 0x7ff3c8c457b8>), _Binding(keys=(Ke
```


*gc.get\_objects* 를 사용할 때의 문제는 객체가 어떻게 할당되는지 아무런 정보도 제공하지 않는다는 점이다. 복잡한 프로그램에서는 객체의 특정 클래스가 여러 방법으로 할당될 수 있다. **객체의 전체 개수는 메모리 누수가 있는 객체 할당 코드를 찾는 것만큼은 중요하지 않다.**


<Br>

## 2. tracemalloc으로 메모리 누수 찾기

파이썬 3.4부터는 새 내장 모듈 [tracemalloc](https://docs.python.org/3/library/tracemalloc.html)으로 이 문제를 해결한다. tracemalloc은 'Trace Memory Allocation'의 약자로, 객체가 할당된 위치에 연결될 수 있도록 해준다. 다음은 tracemalloc을 사용하여 프로그램에서 메모리를 가장 많이 사용하는 세 부분을 출력하는 예다.



```python
import tracemalloc

tracemalloc.start(10)
# 스택 프레임을 최대 10개까지 저장


time1 = tracemalloc.take_snapshot()

for i in range(10000):
    exec('v' + str(i) + ' = ' + str(i))

time2 = tracemalloc.take_snapshot()

stats = time2.compare_to(time1, 'lineno')

for stat in stats[:3]:
    print(stat)


<ipython>:10: size=266 KiB (+266 KiB), count=9743 (+9743), average=28 B
<ipython>:11: size=0 B (-266 KiB), count=0 (-9743)
/home/sunghwanpark/.../mouse_handlers.py:29: size=126 KiB (-6848 B), count=2020 (-107), average=64 B
```

어떤 객체들이 프로그램 메모리 사용량을 주로 차지하고, 소스 코드의 어느 부분에서 할당되는지를 쉽게 알 수 있다.  

<br>

tracemalloc 모듈은 각 할당의 전체 스택 트레이스(stack trace)도 출력할 수 있다.(start 메소드에 넘긴 프레임 개수까지). 다음 코드는 프로그램에서 메모리 사용량의 가장 큰 근원이 되는 부분의 스택 트레이스를 출력한다.

```python
stats = time2.compare_to(time1, 'traceback')
top = stats[0]
print('\n'.join(top.traceback.format()))


  File "<ipython-input-7-c624744ce4eb>", line 10
    exec('v' + str(i) + ' = ' + str(i))
  File "/home/sunghwanpark/.pyenv/versions/3.6.3/lib/python3.6/site-packages/IPython/core/interactiveshell.py", line 2910
    exec(code_obj, self.user_global_ns, self.user_ns)
  File "/home/sunghwanpark/.pyenv/versions/3.6.3/lib/python3.6/site-packages/IPython/core/interactiveshell.py", line 2850
    if self.run_code(code, result):
  File "/home/sunghwanpark/.pyenv/versions/3.6.3/lib/python3.6/site-packages/IPython/core/interactiveshell.py", line 2728
    interactivity=interactivity, compiler=compiler, result=result)
  File "/home/sunghwanpark/.pyenv/versions/3.6.3/lib/python3.6/site-packages/IPython/terminal/interactiveshell.py", line 471
    self.run_cell(code, store_history=True)
  File "/home/sunghwanpark/.pyenv/versions/3.6.3/lib/python3.6/site-packages/IPython/terminal/interactiveshell.py", line 480
    self.interact()
  File "/home/sunghwanpark/.pyenv/versions/3.6.3/lib/python3.6/site-packages/IPython/terminal/ipapp.py", line 356
    self.shell.mainloop()
  File "/home/sunghwanpark/.pyenv/versions/3.6.3/lib/python3.6/site-packages/traitlets/config/application.py", line 658
    app.start()
  File "/home/sunghwanpark/.pyenv/versions/3.6.3/lib/python3.6/site-packages/IPython/__init__.py", line 125
    return launch_new_instance(argv=argv, **kwargs)
  File "/home/sunghwanpark/.pyenv/versions/3.6.3/bin/ipython", line 11
    sys.exit(start_ipython())
```

이와 같은 스택 트레이스는 공통 함수의 어느 부분이 프로그램의 메모리를 많이 소비하는지 알아내는 데 가장 중요한 정보다. 트레이스의 개수가 정확히 10개인 것을 알 수 있는 것도 눈여겨 보자.


<br>

## 3. 핵심 정리

* 파이썬 프로그램이 메모리를 어떻게 사용하고, 메모리 누수를 일으키는지를 이해하기는 어렵다.
* gc 모듈은 어떤 객체가 존재하는지를 이해하는 데 도움을 주지만, 해당 객체가 어떻게 할당되었는지에 대한 정보는 제공하지 않는다.
* 내장 모듈 tracemalloc은 메모리 사용량의 근원을 이해하는 데 필요한 강력한 도구를 제공한다.
* tracemalloc은 파이썬 3.4와 그 이후 버전에서만 사용할 수 있다.
