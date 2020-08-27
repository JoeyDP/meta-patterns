import functools
import warnings


def listenable(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        for listener in self.listeners:
            listener._method_called(method, *args, **kwargs)
        result = method(self, *args, **kwargs)
        for listener in self.listeners:
            listener._method_finished(method, result, *args, **kwargs)

    wrapper.listen = True
    return wrapper


class Listenable:
    class Listener:
        def __init__(self):
            self.subjects = list()

        def unsubscribe_all(self):
            for subject in self.subjects[:]:
                subject.remove_listener(self)

        @staticmethod
        def _get_method_called_name(method):
            return f"on_{method.__name__}"

        @staticmethod
        def _get_method_finished_name(method):
            return f"on_{method.__name__}_finished"

        def _method_called(self, method, *args, **kwargs):
            # Note: Source of notification is purposely not included. If you need to know the source, create a separate listener per source
            name = self._get_method_called_name(method)
            f = getattr(self, name)
            f(*args, **kwargs)

        def _method_finished(self, method, result, *args, **kwargs):
            name = self._get_method_finished_name(method)
            f = getattr(self, name)
            f(result, *args, **kwargs)

        def on_add_listener(self, listener):
            pass

        def on_add_listener_finished(self, subject, listener):
            if self == listener:
                self.subjects.append(subject)

        def on_remove_listener(self, listener):
            pass

        def on_remove_listener_finished(self, subject, listener):
            if self == listener:
                self.subjects.remove(subject)

    def __init__(self, listeners=None):
        self.listeners = list()
        if listeners is not None:
            for listener in listeners:
                self.add_listener(listener)

    @listenable
    def add_listener(self, listener):
        if not isinstance(listener, self.__class__.Listener):
            warnings.warn(f"Listener {listener} not an instance of {self.__class__.Listener}.", RuntimeWarning)
        self.listeners.append(listener)
        return self

    @listenable
    def remove_listener(self, listener):
        self.listeners.remove(listener)
        return self

    def remove_all_listeners(self):
        for listener in self.listeners[:]:
            self.remove_listener(listener)

    def __init_subclass__(cls):
        class Listener(cls.Listener):
            pass

        cls.Listener = Listener
        Listener.__qualname__ = f"{cls.__qualname__}.{Listener.__name__}"

        method_list = [func for name, func in cls.__dict__.items() if
                       callable(func) and not name.startswith("__") and getattr(func, 'listen', False)]

        def _hook(*args, **kwargs):
            pass

        for method in method_list:
            name = cls.Listener._get_method_called_name(method)
            setattr(cls.Listener, name, _hook)
            name = cls.Listener._get_method_finished_name(method)
            setattr(cls.Listener, name, _hook)
