class Vault { void transfer() { int value = 1; } }
class Dispatcher {
    Runnable task;
    void fire() { task.run(); }
}
class Flow {
    Dispatcher d = new Dispatcher();
    void wire() { d.task = () -> new Vault().transfer(); }
    void sink() { d.fire(); }
}
