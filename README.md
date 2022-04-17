# pytest-leak-finder

You have a test that passes when executed alone but fails when running its suite. What's happening? My two cents that some previous test keeps the things dirty. But wich one/s, maybe the previous are a lot, right? 

This plugin helps to find a culprit by doing a [binary search](https://en.wikipedia.org/wiki/Binary_search_algorithm) (*alla* [git bisect](https://git-scm.com/docs/git-bisect)) on the collected tests before the target. 

The first time it will collect the first half of those tests plus the failing one (the target). If the target fails, we are in a good path, so, a new bisect is applied. When the target doesn't fail, it changes the "half" to bisect the next time. 

Consider the following example:

```
$ pytest -v tests/test_demo.py 
collected 6 items                                                                                                                                            
tests/test_demo.py::test1 PASSED                                                                             
tests/test_demo.py::test2 PASSED                                                                              
tests/test_demo.py::test3 PASSED                                                                              
tests/test_demo.py::test4 PASSED                                                                             
tests/test_demo.py::test5 FAILED                                                                              
tests/test_demo.py::test6 PASSED 

$ pytest -v --lf tests/test_demo.py 
collected 6 items / 5 deselected / 1 selected                                                                                                                
tests/test_demo.py::test5 PASSED 

```

You can use leak finder 

On the first run will set the failed test as the "target" and will stop the session.  

```
$ pytest -v --leak-finder tests/test_demo.py 
collected 6 items

tests/test_demo.py::test1 PASSED                                                                              
tests/test_demo.py::test2 PASSED                                                                              
tests/test_demo.py::test3 PASSED                                                                              
tests/test_demo.py::test4 PASSED                                                                              
tests/test_demo.py::test5 FAILED
Leak finder: target set to tests/test_demo.py::test5
```

The second execution will run the first half of the tests passed before the target (let's say the half "A", composed by `test1` and `test2`). 

If the target still fail, that path is followed deeper by dividing again. But in this example 
it passes, so we'll discard it. 

```
$ pytest -v --leak-finder 
collected 6 items / 3 deselected / 3 selected                                                                                                                
tests/test_demo.py::test1 PASSED                                                                              
tests/test_demo.py::test2 PASSED                                                                              
tests/test_demo.py::test5 PASSED
Leak finder: We reach the target and nothing failed. Let's change the last half.
```

A new execution takes the group "B", i.e. `test3` and `test4`.

```
$ pytest -v --leak-finder 
collected 6 items / 3 deselected / 3 selected                                                                                                                
tests/test_demo.py::test3 PASSED                                                                              
tests/test_demo.py::test4 PASSED                                                                              
tests/test_demo.py::test5 FAILED
Leak finder: The group selected still fails. Let's do a new partition.
```


Lastly, a new partition is done and the group "B-A" is taken, i.e. `test3`


```
$ pytest -v --leak-finder 
collected 6 items / 3 deselected / 3 selected                                                                                                                
tests/test_demo.py::test3 PASSED                                                                              
tests/test_demo.py::test5 FAILED
Leak finder: The group selected still fails. Let's do a new partition.
```


And there is it, `test3` is the problematic test we were looking for! 

