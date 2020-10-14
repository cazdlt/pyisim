class Group:
    def __init__(self, session, group=None):
        if group:
            self.name = group["name"]
            self.dn = group["itimDN"]
            self.id = group["id"]
            self.description = group["description"]
            self.profile_name = group["profileName"]
            self.attributes = {
                attr.name: [v for v in attr.values.item]
                for attr in group.attributes.item
            }
