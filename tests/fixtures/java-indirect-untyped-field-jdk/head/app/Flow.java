import java.util.List;

class Vault { void transfer() { int value = 2; } }
class Holder { Runnable task; }
class Flow {
    Holder holder = new Holder();
    List<String> rows;
    void wire() { holder.task = () -> new Vault().transfer(); }
    void sink() { holder.task.run(); rows.size(); }
}
