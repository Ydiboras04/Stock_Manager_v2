from stock.core import ports


def test_in_memory_fakes_implement_every_port_method(repos):
    pairs = [
        (ports.ProductRepository, repos.products),
        (ports.CustomerOrderRepository, repos.customer_orders),
        (ports.PurchaseRequestRepository, repos.purchase_requests),
        (ports.SupplierOrderRepository, repos.supplier_orders),
        (ports.NotificationRepository, repos.notifications),
    ]
    for port, fake in pairs:
        methods = [name for name in vars(port) if not name.startswith("_")]
        assert methods, port
        for name in methods:
            assert callable(getattr(fake, name, None)), f"{type(fake).__name__}.{name}"
