from stock.core.roles import Role


def test_the_two_bpmn_actors():
    assert {role.value for role in Role} == {"STOCK_MANAGER", "PURCHASING_MANAGER"}
