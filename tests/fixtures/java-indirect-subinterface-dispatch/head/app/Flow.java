interface Task extends Runnable {}
class Vault { void transfer() { int value = 2; } }
class Flow {
    Task task;
    void wire() { task = () -> new Vault().transfer(); }
    void sink() { Runnable runnable = task; runnable.run(); }
}
