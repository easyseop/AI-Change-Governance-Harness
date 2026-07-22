import java.util.List;
import java.util.concurrent.ExecutorService;

class Vault { void transfer() { int value = 2; } }
class Flow {
    ExecutorService pool;
    List<String> rows;
    Runnable obtain() { return null; }
    void wire() { pool.submit(() -> new Vault().transfer()); }
    void sink() { obtain().run(); rows.size(); }
}
