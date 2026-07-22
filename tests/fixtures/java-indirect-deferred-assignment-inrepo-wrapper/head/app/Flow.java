class Vault { void transfer() { int value = 2; } }
class Dispatcher { Runnable task; void fire() { task.run(); } }
class Flow {
    Dispatcher d = new Dispatcher();
    void keep(Object value) {}
    void wire() { keep(d.task = () -> new Vault().transfer()); }
    void sink() { d.fire(); }
}
