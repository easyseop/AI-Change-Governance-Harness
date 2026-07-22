interface Left extends Runnable {}
interface Right extends Runnable {}
class Vault { void transfer() { int value = 1; } }
class Flow {
    Left task;
    void wire() { task = () -> new Vault().transfer(); }
    void sink() { Right sibling = (Right) task; sibling.run(); }
}
