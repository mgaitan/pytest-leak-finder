# pytest-leak-finder

You have a test that passes when executed alone but fails when running in the suite. What's happening? My two cents that some previous test keeps the thing dirty. But wich one/s, maybe the previous are a lot, right? 

This plugin helps to find a culprit by doing a [binary search](https://en.wikipedia.org/wiki/Binary_search_algorithm) (*alla* [git bisect](https://git-scm.com/docs/git-bisect)) on the collected tests before the target. 

The first time it will collect the first half of those tests plus the failing one (the target). If the target fails, we are in a good path, so, a new bisect is applied. When the target doesn't fail, it changes the "half" to bisect the next time. 

For example, this could be a tentative way of using. 

```
$ pytest -x

test.py:test1 PASSED
test.py:test2 PASSED
test.py:test3 PASSED
test.py:test4 PASSED
test.py:test5 FAILED

$ pytest --leak-finder test.py:test5

test.py:test1 PASSED
test.py:test2 PASSED
test.py:test5 PASSED

$ pytest --leak-finder test.py:test5

test.py:test3 PASSED
test.py:test4 PASSED
test.py:test5 FAILED


$ pytest --leak-finder test.py:test5

test.py:test3 PASSED
test.py:test5 FAILED
```

`test3` is the needle we were looking for! 

Alternatively, the bisecting could be automatic. 


[1] I'll appreciate your help, @ambro17 😉
