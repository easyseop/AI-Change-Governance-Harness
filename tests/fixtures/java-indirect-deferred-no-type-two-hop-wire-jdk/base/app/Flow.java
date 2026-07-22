import java.util.List;

class Vault { void transfer() { int value = 1; } }
class Inner { Runnable task; void fire() { task.run(); } }
class Outer { Inner inner = new Inner(); void go() { inner.fire(); } }
class Flow {
    Outer o = new Outer();
    List<String> rows;
    void wire() { rows.size(); o.inner.task = () -> new Vault().transfer(); }
    void sink() { o.go(); }
}
