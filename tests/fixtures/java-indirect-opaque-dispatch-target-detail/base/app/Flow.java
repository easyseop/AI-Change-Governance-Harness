import java.util.List;

interface Job { void run(); }
class Ledger { void post() { int value = 1; } }
class Flow {
    Job job = () -> new Ledger().post();
    List<String> rows;
    void sink() { rows.size(); }
}
