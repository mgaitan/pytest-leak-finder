# pytest-leak-finder

[![PyPI version](https://img.shields.io/pypi/v/pytest-leak-finder.svg)](https://pypi.org/project/pytest-leak-finder)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-leak-finder.svg)](https://pypi.org/project/pytest-leak-finder)
[![CI](https://github.com/mgaitan/pytest-leak-finder/actions/workflows/ci.yml/badge.svg)](https://github.com/mgaitan/pytest-leak-finder/actions/workflows/ci.yml)


You have a test that passes when executed alone but fails when running its suite. What's happening? My two cents that some previous test keeps the things dirty. But wich one/s, maybe the previous are a lot, right? 

This plugin helps to find a culprit by doing a [binary search](https://en.wikipedia.org/wiki/Binary_search_algorithm) (*alla* [git bisect](https://git-scm.com/docs/git-bisect)) on the collected tests before the target. 

The first time it will collect the first half of those tests plus the failing one (the target). If the target fails, we are in a good path, so, a new bisect is applied. When the target doesn't fail, it changes the "half" to bisect the next time. 

Consider the following example:

```
$ pytest -v demo/test_demo.py 
collected 6 items                                                                                                                                            
tests/test_demo.py::test1 PASSED                                                                             
tests/test_demo.py::test2 PASSED                                                                              
tests/test_demo.py::test3 PASSED                                                                              
tests/test_demo.py::test4 PASSED                                                                             
tests/test_demo.py::test5 FAILED                                                                              
tests/test_demo.py::test6 PASSED 

$ pytest -v --lf demo/test_demo.py 
collected 6 items / 5 deselected / 1 selected                                                                                                                
tests/test_demo.py::test5 PASSED 

```

You can use pytest-leak-finder to find the problematic test. 

On the first run will set the failed test as the "target" and will stop the session.  

```
$ pytest -v --leak-finder demo/test_demo.py 
collected 6 items

tests/test_demo.py::test1 PASSED                                                                              
tests/test_demo.py::test2 PASSED                                                                              
tests/test_demo.py::test3 PASSED                                                                              
tests/test_demo.py::test4 PASSED                                                                              
tests/test_demo.py::test5 FAILED

===================================================== Leak finder =====================================================
Target set to: pytest-leak-finder/tests/test_demo.py::test5

Next step: a
Current target is: pytest-leak-finder/tests/test_demo.py::test5
============================================= 1 failed, 4 passed in 0.13s =============================================
```

The second execution will run the first half of the tests passed before the target (step "a", composed by `test1` and `test2`). 

If the target still fail, that path would followed deeper by dividing again. But in this example 
it passes, so we'll discard it, and asumme the other half was the one that include the leak.
That's the reason why the "next step" will be "ba".

```
$ pytest -v --leak-finder demo/test_demo.py
collected 6 items / 3 deselected / 3 selected                                                                                                                
demo/test_demo.py::test1 PASSED                                                                                 [ 33%]
demo/test_demo.py::test2 PASSED                                                                                 [ 66%]
demo/test_demo.py::test5 PASSED                                                                                 [100%]


===================================================== Leak finder =====================================================
We reach the target and nothing failed. Let's change the last half.

Next step: ba
Current target is: pytest-leak-finder/demo/test_demo.py::test5
=========================================== 3 passed, 3 deselected in 0.03s ===========================================
```


So, the new step will be "B-A", i.e. `test3`


```
$ pytest -v --leak-finder demo/test_demo.py
collected 6 items / 3 deselected / 3 selected                                                                                                                
tests/test_demo.py::test3 PASSED                                                                              
tests/test_demo.py::test5 FAILED

===================================================== Leak finder =====================================================
We found a leak!

Leak found in: pytest-leak-finder/demo/test_demo.py::test3
Last step was: ba
```


And there it is, `test3` was the problematic test we were looking for! 
