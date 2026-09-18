"""
Smart Contract — IP Registry on Tezos
Deploy via SmartPy IDE: https://smartpy.io/ide

Stores SHA-256 hashes of intellectual property assets on-chain.
Single register, batch register, master hash (one-tx portfolio proof),
and ownership transfer.
"""

import smartpy as sp


@sp.module
def main():
    class IPRegistry(sp.Contract):
        """
        Intellectual property registry on Tezos.
        Stores SHA-256 hashes with metadata.
        Only the owner can register entries.
        """

        def __init__(self, owner):
            self.data.owner = owner
            self.data.registry = sp.big_map()
            self.data.total_entries = 0
            self.data.master_hash = sp.bytes("0x")

        @sp.entrypoint
        def register(self, params):
            """Register a single hash on-chain."""
            assert sp.sender == self.data.owner, "NOT_OWNER"
            assert not self.data.registry.contains(params.code), "ALREADY_REGISTERED"

            self.data.registry[params.code] = sp.record(
                sha256=params.sha256,
                description=params.description,
                timestamp=sp.now,
                block_level=sp.level,
            )
            self.data.total_entries += 1

        @sp.entrypoint
        def register_batch(self, params):
            """Register multiple hashes in one transaction (gas savings)."""
            assert sp.sender == self.data.owner, "NOT_OWNER"

            for entry in params.entries:
                assert not self.data.registry.contains(entry.code), "DUPLICATE"
                self.data.registry[entry.code] = sp.record(
                    sha256=entry.sha256,
                    description=entry.description,
                    timestamp=sp.now,
                    block_level=sp.level,
                )
                self.data.total_entries += 1

        @sp.entrypoint
        def set_master_hash(self, params):
            """Set master hash (hash of all hashes) — single-tx portfolio proof."""
            assert sp.sender == self.data.owner, "NOT_OWNER"
            self.data.master_hash = params.hash

        @sp.entrypoint
        def transfer_ownership(self, params):
            """Transfer registry ownership."""
            assert sp.sender == self.data.owner, "NOT_OWNER"
            self.data.owner = params.new_owner


# ===================================================================
# TESTS
# ===================================================================

@sp.add_test()
def test():
    scenario = sp.test_scenario("IP Registry Test", main)
    scenario.h1("IP Registry")

    owner = sp.address("tz1exampleOwnerAddressXXXXXXXXXXXXXXX")
    attacker = sp.address("tz1exampleAttackerAddrXXXXXXXXXXXXXXX")

    contract = main.IPRegistry(owner)
    scenario += contract

    # Test: register single entry
    scenario.h2("Register single entry")
    contract.register(
        code="EXAMPLE-ASSET",
        sha256=sp.bytes("0xaabbccdd"),
        description="Example intellectual property asset",
        _sender=owner,
    )
    scenario.verify(contract.data.total_entries == 1)

    # Test: register batch
    scenario.h2("Register batch")
    contract.register_batch(
        entries=[
            sp.record(code="ASSET-A", sha256=sp.bytes("0x1111"), description="First asset"),
            sp.record(code="ASSET-B", sha256=sp.bytes("0x2222"), description="Second asset"),
            sp.record(code="ASSET-C", sha256=sp.bytes("0x3333"), description="Third asset"),
        ],
        _sender=owner,
    )
    scenario.verify(contract.data.total_entries == 4)

    # Test: unauthorized register blocked
    scenario.h2("Unauthorized blocked")
    contract.register(
        code="HACK",
        sha256=sp.bytes("0xdead"),
        description="Should fail",
        _sender=attacker,
        _valid=False,
    )

    # Test: duplicate blocked
    scenario.h2("Duplicate blocked")
    contract.register(
        code="EXAMPLE-ASSET",
        sha256=sp.bytes("0xffff"),
        description="Duplicate",
        _sender=owner,
        _valid=False,
    )

    # Test: master hash
    scenario.h2("Set master hash")
    contract.set_master_hash(
        hash=sp.bytes("0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"),
        _sender=owner,
    )

    # Test: transfer ownership
    scenario.h2("Transfer ownership")
    new_owner = sp.address("tz1exampleNewOwnerAddrXXXXXXXXXXXXXXX")
    contract.transfer_ownership(new_owner=new_owner, _sender=owner)
    scenario.verify(contract.data.owner == new_owner)
