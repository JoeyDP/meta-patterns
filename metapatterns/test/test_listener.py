import pytest

from metapatterns import Listenable, listenable


@pytest.fixture
def subject():
    class Subject(Listenable):
        def __init__(self, listeners=None):
            super().__init__(listeners)
            self.myfunc_called = False
            self.myfunc_arg = None

            self.myfunc2_called = False
            self.myfunc2_arg = None

        @listenable
        def myfunc(self, arg):
            self.myfunc_arg = arg
            self.myfunc_called = True
            return arg * 2

        def myfunc2(self, arg):
            self.myfunc2_arg = arg
            self.myfunc2_called = True
            return arg * 4

    return Subject()


@pytest.fixture
def subject_listener(subject):
    class MyListener(subject.__class__.Listener):
        def __init__(self):
            super().__init__()
            self.myfunc_called = False
            self.myfunc_arg = None
            self.myfunc_res = None
            self.myfunc2_called = False

        def on_myfunc(self, arg):
            self.myfunc_called = True
            self.myfunc_arg = arg

        def on_myfunc_finished(self, result, arg):
            assert self.myfunc_arg == arg
            self.myfunc_res = result

        def on_myfunc2(self, arg):
            """ Should not be called """
            self.myfunc2_called = True

    return MyListener()


def test_without_listener(subject):
    assert not subject.myfunc_called and subject.myfunc_arg == None
    assert not subject.myfunc2_called and subject.myfunc2_arg == None

    subject.myfunc(3)
    assert subject.myfunc_called and subject.myfunc_arg == 3
    assert not subject.myfunc2_called and subject.myfunc2_arg == None

    subject.myfunc2(9)
    assert subject.myfunc_called and subject.myfunc_arg == 3
    assert subject.myfunc2_called and subject.myfunc2_arg == 9


def test_add_listener(subject, subject_listener):
    assert not subject.myfunc_called and subject.myfunc_arg == None
    assert not subject.myfunc2_called and subject.myfunc2_arg == None

    subject.add_listener(subject_listener)
    assert subject in subject_listener.subjects

    subject.myfunc(3)

    assert subject.myfunc_called and subject.myfunc_arg == 3
    assert not subject.myfunc2_called and subject.myfunc2_arg == None
    assert subject_listener.myfunc_called and subject_listener.myfunc_arg == 3 and subject_listener.myfunc_res == 6
    assert not subject_listener.myfunc2_called

    subject.myfunc2(9)

    assert subject.myfunc_called and subject.myfunc_arg == 3
    assert subject.myfunc2_called and subject.myfunc2_arg == 9
    assert not subject_listener.myfunc2_called


def test_remove_listener(subject, subject_listener):
    subject.add_listener(subject_listener)
    subject.remove_listener(subject_listener)
    subject.myfunc(3)

    assert subject.myfunc_called and subject.myfunc_arg == 3
    assert not subject.myfunc2_called and subject.myfunc2_arg == None
    assert not subject_listener.myfunc_called
    assert not subject_listener.myfunc2_called

    subject.myfunc2(9)

    assert subject.myfunc_called and subject.myfunc_arg == 3
    assert subject.myfunc2_called and subject.myfunc2_arg == 9
    assert not subject_listener.myfunc_called
    assert not subject_listener.myfunc2_called


def test_remove_unregistered_listener(subject, subject_listener):
    with pytest.raises(ValueError):
        subject.remove_listener(subject_listener)


def test_init_listeners(subject, subject_listener):
    """ Create object again, with list of listeners """
    subject = subject.__class__([subject_listener])
    assert subject in subject_listener.subjects

    subject.myfunc(3)

    assert subject.myfunc_called and subject.myfunc_arg == 3
    assert not subject.myfunc2_called and subject.myfunc2_arg == None
    assert subject_listener.myfunc_called and subject_listener.myfunc_arg == 3 and subject_listener.myfunc_res == 6
    assert not subject_listener.myfunc2_called

    subject.myfunc2(9)

    assert subject.myfunc_called and subject.myfunc_arg == 3
    assert subject.myfunc2_called and subject.myfunc2_arg == 9
    assert not subject_listener.myfunc2_called


def test_multiple_listeners(subject, subject_listener):
    subject_listener2 = subject_listener.__class__()
    subject.add_listener(subject_listener)
    assert subject in subject_listener.subjects
    subject.add_listener(subject_listener2)
    assert subject in subject_listener2.subjects

    subject.myfunc(3)

    assert subject_listener.myfunc_called and subject_listener.myfunc_arg == 3 and subject_listener.myfunc_res == 6
    assert not subject_listener.myfunc2_called
    assert subject_listener2.myfunc_called and subject_listener2.myfunc_arg == 3 and subject_listener2.myfunc_res == 6
    assert not subject_listener2.myfunc2_called


def test_remove_all(subject, subject_listener):
    subject_listener2 = subject_listener.__class__()
    subject.add_listener(subject_listener)
    assert subject in subject_listener.subjects
    subject.add_listener(subject_listener2)
    assert subject in subject_listener2.subjects

    subject.remove_all_listeners()

    subject.myfunc(3)

    assert not subject_listener.myfunc_called
    assert not subject_listener2.myfunc_called


def test_unsubscribe_all(subject, subject_listener):
    subject2 = subject.__class__()
    subject.add_listener(subject_listener)
    subject2.add_listener(subject_listener)

    subject_listener.unsubscribe_all()

    subject.myfunc(3)
    subject2.myfunc(3)

    assert not subject_listener.myfunc_called


def test_listen_subclass(subject):
    class SubSubject(subject.__class__):
        def __init__(self, listeners=None):
            super().__init__(listeners)
            self.myfunc3_called = False
            self.myfunc3_arg = None

        @listenable
        def myfunc3(self, arg):
            self.myfunc3_arg = arg
            self.myfunc3_called = True
            return arg * 10

    class SubSubjectListener(SubSubject.Listener):
        def __init__(self):
            super().__init__()
            self.myfunc3_called = False
            self.myfunc3_arg = None
            self.myfunc3_res = None

        def on_myfunc3(self, arg):
            self.myfunc3_called = True
            self.myfunc3_arg = arg

        def on_myfunc3_finished(self, result, arg):
            assert self.myfunc3_arg == arg
            self.myfunc3_res = result

    subsubject_listener = SubSubjectListener()
    subject.add_listener(subsubject_listener)
    subject.myfunc(3)

    subsubject = SubSubject()
    subsubject.add_listener(subsubject_listener)

    subsubject.myfunc3(5)
    assert subsubject_listener.myfunc3_called
    assert subsubject_listener.myfunc3_arg == 5
    assert subsubject_listener.myfunc3_res == 50


def test_error_on_without_target():
    class Subject(Listenable):
        def test_finished(self):
            pass

    with pytest.raises(TypeError):
        class Listener1(Subject.Listener):
            def on_test(self):
                pass

    with pytest.raises(TypeError):
        class Listener2(Subject.Listener):
            def on_test_finished(self):
                pass


def test_error_on_with_target_different_subject(subject):
    class Subject1(Listenable):
        pass

    class Subject2(Listenable):
        @listenable
        def myfunc(self):
            pass

    with pytest.raises(TypeError):
        class Listener1(Subject1.Listener):
            def on_myfunc(self):
                pass

            def on_myfunc_finished(self):
                pass

    class Listener2(Subject2.Listener):
        def on_myfunc(self):
            pass

        def on_myfunc_finished(self):
            pass

    class Listener3(Subject1.Listener, Subject2.Listener):
        def on_myfunc(self):
            pass

        def on_myfunc_finished(self):
            pass
