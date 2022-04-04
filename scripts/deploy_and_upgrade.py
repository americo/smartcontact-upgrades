from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    Contract,
    network,
    Box,
    BoxV2,
    ProxyAdmin,
    TransparentUpgradeableProxy,
)


def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy({"from": account}, publish_source=True)

    proxy_admin = ProxyAdmin.deploy({"from": account}, publish_source=True)

    # initializer = box.store, 1
    box_encoded_initializer_function = encode_function_data()

    # Turn Box contract upgradeable, saving it into proxy
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
        publish_source=True,
    )

    print(f"Proxy deployeds to {proxy}, you can now upgrade to v2!")

    # Accessing the Box contract by abi and getting proxy address, it allows us to interact with Box contract using proxy
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(1, {"from": account})
    print(proxy_box.retrieve())

    # Deploying upgrade of Box contract
    box_v2 = BoxV2.deploy({"from": account}, publish_source=True)

    # Upgrading the proxy with a new contract
    upgrade_transaction = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    print("Proxy has been upgraded!")

    # Accessing the new Box contract by abi and getting proxy address, it allows us to interact with Box V2 contract using proxy
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})
    print(proxy_box.retrieve())
