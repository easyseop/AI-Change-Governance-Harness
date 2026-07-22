interface Task extends Runnable {}
class Vault { void transfer() { int value = 2; } }
class Flow {
    Runnable task;
    void wire() { task = () -> new Vault().transfer(); }
    void sink() { Task narrowed = (Task) task; narrowed.run(); }
}
