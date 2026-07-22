import java.util.List;

class Vault { void transfer() { int value = 1; } }
class Flow {
    Runnable task;
    List<String> rows;
    void wire() { task = () -> new Vault().transfer(); }
    Runnable obtain() { return task; }
    void sink() { obtain().run(); rows.size(); }
}
