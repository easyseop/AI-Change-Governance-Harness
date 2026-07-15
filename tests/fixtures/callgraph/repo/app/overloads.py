def foo():
    return "module"


class C:
    def foo(self):
        return "class"


def bar():
    return foo()
