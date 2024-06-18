from daaily_v2.enums import Environment
from daaily_v2.lucy.client import Client as LucyClient

# APIS

lucy_client = LucyClient(Environment.STAGING)

manufacturer = lucy_client.get_manufacturer(31000389)
manufacturers = lucy_client.get_manufacturers([3100089, 3103523])
print(manufacturer.get("name"))
print([m.get("name") for m in manufacturers])

distributor = lucy_client.get_distributor(10027550)
distributors = lucy_client.get_distributors([10027550, 8201493])
print(distributor.get("name"))
print([d.get("name") for d in distributors])
