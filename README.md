# meta-patterns
Design patterns for Python implemented with decorators and classes.


## Getting Started

Currently only one design pattern is implemented: `Listener`.

#### Listener Pattern

The `Listener` pattern (otherwise known as the `Observer` or `Publish-Subscribe` pattern) is a behavioral design pattern that lets you define a subscription mechanism to notify multiple objects about any events that happen to the object they’re observing ([source](https://refactoring.guru/design-patterns/observer)).


Its use is demonstrated here:

```python
from metapatterns.listener import Listenable, listenable


class Subject(Listenable):
    @listenable
    def myfunc(self, arg1):
        """
        @listenable indicates this function can be 'listened in on'.
        It allows Listeners to hook into it (see MyListener)
        """
        print("myfunc called with arg", arg1)
        return "Hoozah"

    def myfunc2(self, arg1):
        print("myfunc called with arg", arg1)


class MyListener(Subject.Listener):
    """
    Identify this class as a listener of `Subject` through inheritance.
    This makes it so not all listenable methods need to be implemented (they have a default empty implementation in `Subject.Listener`).
    """
    def on_myfunc(self, arg1):
        print("listened in on call to myfunc with arg", arg1)

    def on_myfunc_finished(self, result, arg1):
        print("listened in on result of myfunc with arg", arg1, "and result", result)

    # This cannot be defined because myfunc2 is not a listenable function in Subject
    #def on_myfunc2(self, arg1):
        #pass
```

We can run this as follows:

```python
if __name__ == "__main__":
    subject = Subject()
    print("# Calling myfunc without listener")
    subject.myfunc(3)

    listener = MyListener()
    subject.add_listener(listener)

    print("\n# Calling myfunc with listener")
    subject.myfunc(5)

    print("\n# Calling myfunc2 with listener")
    subject.myfunc2(7)

    subject.remove_listener(listener)

    print("\n# Calling myfunc again with listener removed")
    subject.myfunc(5)
```

which gives the output:

```console
# Calling myfunc without listener
myfunc called with arg 3

# Calling myfunc with listener
listened in on call to myfunc with arg 5
myfunc called with arg 5
listened in on result of myfunc with arg 5 and result Hoozah

# Calling myfunc2 with listener
myfunc called with arg 7

# Calling myfunc again with listener removed
myfunc called with arg 5
```

Subclassing from `Subject.Listener` has the advantage of raising a `TypeError` when an `on_` function has no matching counterpart in `Subject`. This can help detect difficult to find problems that arise when changing the name of a function in `Subject`. Our method includes this check to guard against some issues that come with the loose coupling of the `Listener` pattern.


## Future Work
 - Implement more design patterns.
 - Suggestions? Contact [me](mailto:joeydepauw@gmail.com)!
