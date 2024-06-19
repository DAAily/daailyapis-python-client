from daaily_v2.enums import Environment
from daaily_v2.lucy.client import Client as LucyClient

# APIS

lucy_client = LucyClient(Environment.STAGING)

manufacturer = lucy_client.get_manufacturer(3100089)
manufacturers = lucy_client.get_manufacturers([3100089, 3103523])
u_manufacturers = lucy_client.update_manufacturers([manufacturer])
print("Manufacturer name:", manufacturer.get("name"))
print("Manufacturer names:", [m.get("name") for m in manufacturers])
print("Manufacturer updates:", [m.get("name") for m in u_manufacturers])

distributor = lucy_client.get_distributor(10027550)
distributors = lucy_client.get_distributors([10027550, 8201493])
u_distributors = lucy_client.update_distributors([distributor])
print("Distributor name:", distributor.get("name"))
print("Distributor names:", [d.get("name") for d in distributors])
print("Distributor updates:", [d.get("name") for d in u_distributors])

journalist = lucy_client.get_journalist(10027574)
journalists = lucy_client.get_journalists(journalist_ids=[10027574, 10027583])
u_journalists = lucy_client.update_journalists([journalist])
print("Journalist name:", journalist.get("name"))
print("Journalist names:", [j.get("name") for j in journalists])
print("Journalist updates:", [j.get("name") for j in u_journalists])

project = lucy_client.get_project(20027116)
projects = lucy_client.get_projects(project_ids=[20027116, 20027118])
u_projects = lucy_client.update_projects([project])
print("Project name:", project.get("name_en"))
print("Project names:", [p.get("name_en") for p in projects])
print("Project updates:", [p.get("name_en") for p in u_projects])

product = lucy_client.get_product(20001357)
products = lucy_client.get_products(product_ids=[20001357, 20138916])
u_products = lucy_client.update_products([product])
print("Product name:", product.get("name_en"))
print("Product names:", [p.get("name_en") for p in products])
print("Product updates:", [p.get("name_en") for p in u_products])

family = lucy_client.get_family(20701087)
families = lucy_client.get_families(family_ids=[20701087, 20701088])
u_families = lucy_client.update_families([family])
print("Family name:", family.get("name_en"))
print("Family names:", [f.get("name_en") for f in families])
print("Family updates:", [f.get("name_en") for f in u_families])

creator = lucy_client.get_creator(5200003)
creators = lucy_client.get_creators(creator_ids=[5200003, 5200020])
u_creators = lucy_client.update_creators([creator])
print("Creator name:", creator.get("name"))
print("Creator names:", [c.get("name") for c in creators])
print("Creator updates:", [c.get("name") for c in u_creators])

filter = lucy_client.get_filter(10000451)
filters = lucy_client.get_filters(filter_ids=[10000451, 10000449])
u_filters = lucy_client.update_filters([filter])
print("Filter name:", filter.get("name_en"))
print("Filter names:", [f.get("name_en") for f in filters])
print("Filter updates:", [f.get("name_en") for f in u_filters])

story = lucy_client.get_story(7001901)
stories = lucy_client.get_stories(story_ids=[7001901, 7001917])
u_stories = lucy_client.update_stories([story])
print("Story name:", story.get("name_en"))
print("Story names:", [s.get("name_en") for s in stories])
print("Story updates:", [s.get("name_en") for s in u_stories])

group = lucy_client.get_group(7031247)
groups = lucy_client.get_groups(group_ids=[7031247, 3249984])
u_groups = lucy_client.update_groups([group])
print("Group name:", group.get("name_en"))
print("Group names:", [g.get("name_en") for g in groups])
print("Group updates:", [g.get("name_en") for g in u_groups])

fair = lucy_client.get_fair(10027586)
fairs = lucy_client.get_fairs(fair_ids=[10027586, 10027587])
u_fairs = lucy_client.update_fairs([fair])
print("Fair name:", fair.get("name"))
print("Fair names:", [f.get("name") for f in fairs])
print("Fair updates:", [f.get("name") for f in u_fairs])
