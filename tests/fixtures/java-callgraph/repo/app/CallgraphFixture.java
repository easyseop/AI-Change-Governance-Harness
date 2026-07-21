package app;

interface PaymentPort {
    void pay();
}

class CardPayment implements PaymentPort {
    public void pay() {}
}

class RegionalCardPayment extends CardPayment {
    public void pay() {}
}

class WirePayment implements PaymentPort {
    public void pay() {}
}

class BillingService {
    @Autowired
    PaymentPort injected;

    private final PaymentPort constructed;

    BillingService(PaymentPort constructed) {
        this.constructed = constructed;
    }

    @Transactional
    void billInjected() {
        injected.pay();
    }

    void billConstructed() {
        constructed.pay();
    }

    void reflect(Method method, Object target) throws Exception {
        method.invoke(target);
    }
}
