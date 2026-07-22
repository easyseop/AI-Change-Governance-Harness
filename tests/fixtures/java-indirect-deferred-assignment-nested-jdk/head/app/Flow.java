import java.util.List;

class Vault { void transfer() { int value = 2; } }
class Dispatcher { Runnable task; void fire() { task.run(); } }
class Flow {
    Dispatcher d = new Dispatcher();
    List<String> rows;
    void wire() { rows.add(String.valueOf(d.task = () -> new Vault().transfer())); }
    void sink() { d.fire(); }
}
