import functools
import warnings


def listenable(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        self._method_called(method, *args, **kwargs)
        result = method(self, *args, **kwargs)
        self._method_finished(method, result, *args, **kwargs)

    wrapper.listen = True
    return wrapper


class Listenable:
    class Listener:
        def __init__(self):
            self.subjects = list()

        def unsubscribe_all(self):
            for subject in self.subjects[:]:
                subject.remove_listener(self)

        def __init_subclass__(listener_cls, **kwargs):
            super().__init_subclass__(**kwargs)
            listener_cls._check_targets()

        @classmethod
        def _get_target_methods(cls):
            targets = {name for name, func in Listenable.__dict__.items() if
                       callable(func) and getattr(func, 'listen', False)}
            return targets

        @classmethod
        def _check_targets(cls):
            """ Verify that functions with `on_` have a counterpart in subject_cls. """
            hooks = {name[len("on_"):] for name, func in cls.__dict__.items() if callable(func) and name.startswith("on_")}
            hooks = {name[:-len("_finished")] if name.endswith("_finished") else name for name in hooks}
            targets = cls._get_target_methods()
            unmatched = hooks - targets
            if len(unmatched) > 0:
                raise TypeError(f"{cls} tries to listen to the following functions, which don't exist in their subject: {unmatched}")

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

    def __init__(self, listeners=None, **kwargs):
        super().__init__(**kwargs)
        self.listeners = list()
        if listeners is not None:
            for listener in listeners:
                # explicitly call add_listener.
                self.add_listener(listener)

    @listenable
    def add_listener(self, listener):
        if not isinstance(listener, Listenable.Listener):
            warnings.warn(f"Listener {listener} not an instance of {Listenable.Listener}.", RuntimeWarning)
        self.listeners.append(listener)
        return self

    @listenable
    def remove_listener(self, listener):
        self.listeners.remove(listener)
        return self

    def remove_all_listeners(self):
        for listener in self.listeners[:]:
            self.remove_listener(listener)

    @staticmethod
    def _get_method_called_name(method):
        return f"on_{method.__name__}"

    @staticmethod
    def _get_method_finished_name(method):
        return f"on_{method.__name__}_finished"

    def _method_called(self, method, *args, **kwargs):
        # Note: Source of notification is purposely not included. If you need to know the source, create a separate listener per source
        name = self._get_method_called_name(method)
        for listener in self.listeners:
            f = getattr(listener, name, None)
            if f is not None:
                f(*args, **kwargs)

    def _method_finished(self, method, result, *args, **kwargs):
        name = self._get_method_finished_name(method)
        for listener in self.listeners:
            f = getattr(listener, name, None)
            if f is not None:
                f(result, *args, **kwargs)

    def __init_subclass__(subject_cls, **kwargs):
        super().__init_subclass__(**kwargs)
        class Listener(subject_cls.Listener):
            @classmethod
            def _get_target_methods(listener_cls):
                methods = super()._get_target_methods()
                targets = {name for name, func in subject_cls.__dict__.items() if
                               callable(func) and getattr(func, 'listen', False)}
                methods.update(targets)
                return methods

        subject_cls.Listener = Listener
        Listener.__qualname__ = f"{subject_cls.__qualname__}.{Listener.__name__}"

        method_list = [func for name, func in subject_cls.__dict__.items() if
                       callable(func) and getattr(func, 'listen', False)]

        def _hook(*args, **kwargs):
            pass

        for method in method_list:
            name = subject_cls._get_method_called_name(method)
            setattr(subject_cls.Listener, name, _hook)
            name = subject_cls._get_method_finished_name(method)
            setattr(subject_cls.Listener, name, _hook)
