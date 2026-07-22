import java.util.Objects;

class Vault { void transfer() { int value = 2; } }
class Dispatcher { Runnable task; void fire() { task.run(); } }
class Flow {
    Dispatcher d = new Dispatcher();
    void wire() { Objects.requireNonNull((Runnable) () -> hashCode()); d.task = () -> new Vault().transfer(); }
    void sink() { d.fire(); }
}
