import asyncio
from pysnmp.hlapi.v3arch.asyncio import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    get_cmd,
    next_cmd,
)


async def snmp_get(ip: str, oid: str, community: str = 'public', port: int = 161):
    transport = await UdpTransportTarget.create((ip, port))
    errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
        SnmpEngine(),
        CommunityData(community, mpModel=1),
        transport,
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
    )

    if errorIndication:
        print(f"SNMP GET Error: {errorIndication}")
        return None
    if errorStatus:
        print(f"SNMP GET Error: {errorStatus.prettyPrint()} at {errorIndex}")
        return None

    return str(varBinds[0][1])


async def snmp_walk(ip: str, base_oid: str, community: str = 'public', port: int = 161):
    transport = await UdpTransportTarget.create((ip, port))
    results = []
    current_oid = ObjectIdentity(base_oid)

    while True:
        errorIndication, errorStatus, errorIndex, varBinds = await next_cmd(
            SnmpEngine(),
            CommunityData(community, mpModel=1),
            transport,
            ContextData(),
            ObjectType(current_oid),
            lexicographicMode=True,
        )

        if errorIndication:
            print(f"SNMP WALK Error: {errorIndication}")
            break
        if errorStatus:
            print(f"SNMP WALK Error: {errorStatus.prettyPrint()} at {errorIndex}")
            break

        oid, value = varBinds[0]
        if not str(oid).startswith(base_oid):
            # Stop if we've moved out of the base subtree
            break

        results.append(f"{oid} = {value}")
        current_oid = ObjectIdentity(str(oid))  # Move to next OID

    return results


async def main():
    ip = "127.0.0.1"
    community = "public"

    sys_descr_oid = "1.3.6.1.2.1.1.1.0"
    sys_descr = await snmp_get(ip, sys_descr_oid, community)
    print(f"SNMP GET sysDescr: {sys_descr}")

    print("\nSNMP WALK system group:")
    walk_results = await snmp_walk(ip, "1.3.6.1.2.1.1", community)
    for entry in walk_results:
        print(entry)


if __name__ == "__main__":
    asyncio.run(main())
 