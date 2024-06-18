from daaily_v2.enums import Environment
from daaily_v2.lucy.client import Client as LucyClient

# APIS

lucy_client = LucyClient(Environment.STAGING)

manufacturer = lucy_client.get_manufacturer(3100089)
manufacturers = lucy_client.get_manufacturers([3100089, 3103523])
print("Manufacturer name:", manufacturer.get("name"))
print("Manufacturer names:", [m.get("name") for m in manufacturers])

distributor = lucy_client.get_distributor(10027550)
distributors = lucy_client.get_distributors([10027550, 8201493])
print("Distributor name:", distributor.get("name"))
print("Distributor names:", [d.get("name") for d in distributors])

journalist = lucy_client.get_journalist(10027574)
journalists = lucy_client.get_journalists(journalist_ids=[10027574, 10027583])
print("Journalist name:", journalist.get("name"))
print("Journalist names:", [j.get("name") for j in journalists])

project = lucy_client.get_project(20027116)
projects = lucy_client.get_projects(project_ids=[20027116, 20027118])
print("Project name:", project.get("name_en"))
print("Project names:", [p.get("name_en") for p in projects])

product = lucy_client.get_product(20001357)
products = lucy_client.get_products(product_ids=[20001357, 20138916])
print("Product name:", product.get("name_en"))
print("Product names:", [p.get("name_en") for p in products])

family = lucy_client.get_family(20701087)
families = lucy_client.get_families(family_ids=[20701087, 20701088])
print("Family name:", family.get("name_en"))
print("Family names:", [f.get("name_en") for f in families])

creator = lucy_client.get_creator(5200003)
creators = lucy_client.get_creators(creator_ids=[5200003, 5200020])
print("Creator name:", creator.get("name"))
print("Creator names:", [c.get("name") for c in creators])

filter = lucy_client.get_filter(10000451)
filters = lucy_client.get_filters(filter_ids=[10000451, 10000449])
print("Filter name:", filter.get("name_en"))
print("Filter names:", [f.get("name_en") for f in filters])

story = lucy_client.get_story(7001901)
stories = lucy_client.get_stories(story_ids=[7001901, 7001917])
print("Story name:", story.get("name_en"))
print("Story names:", [s.get("name_en") for s in stories])

group = lucy_client.get_group(7031247)
groups = lucy_client.get_groups(group_ids=[7031247, 3249984])
print("Group name:", group.get("name_en"))
print("Group names:", [g.get("name_en") for g in groups])

fair = lucy_client.get_fair(10027586)
fairs = lucy_client.get_fairs(fair_ids=[10027586, 10027587])
print("Fair name:", fair.get("name"))
print("Fair names:", [f.get("name") for f in fairs])
