from metapatterns.listener import Listenable, listenable


class Subject(Listenable):
    @listenable
    def myfunc(self, arg1):
        """ @listenable indicates this function can be 'listened in on'. It allows Listeners to hook into it (see MyListener) """
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

    def on_myfunc2(self, arg1):
        """ This will not be called by the subject, because `myfunc2` is not a listenable function. """
        print("listened in on call to myfunc2 with arg", arg1)


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
