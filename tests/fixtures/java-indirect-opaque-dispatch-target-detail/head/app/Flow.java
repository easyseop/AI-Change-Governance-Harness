import java.util.List;

interface Job { void run(); }
class Ledger { void post() { int value = 2; } }
class Flow {
    Job job = () -> new Ledger().post();
    List<String> rows;
    void sink() { rows.size(); }
}
