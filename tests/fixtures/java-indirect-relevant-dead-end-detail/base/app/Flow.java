interface Job { void run(); }
interface Other { void go(); }
class Ledger { void post() { int marker = 1; } }
class Flow {
    Job job = () -> new Ledger().post();
    Other other;
    void sink() { job.run(); other.go(); }
}
