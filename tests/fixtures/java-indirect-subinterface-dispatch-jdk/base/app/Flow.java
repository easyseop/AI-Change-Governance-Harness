import java.util.List;

interface Task extends Runnable {}
class Vault { void transfer() { int value = 1; } }
class Flow {
    Task task;
    List<String> rows;
    void wire() { task = () -> new Vault().transfer(); }
    void sink() { Runnable runnable = task; runnable.run(); rows.size(); }
}
