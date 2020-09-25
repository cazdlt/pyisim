def activity_batch_complete(session, actividades, resultado, justification):

    acts_dict = []

    for act in actividades:
        if act.status == "PENDING":
            act_dict = {"_attributes": {}, "_links": {"workitem": {}}}
            act_dict["_attributes"]["type"] = act.type
            act_dict["_attributes"]["name"] = act.name
            act_dict["_links"]["workitem"]["href"] = act.workitem_href

            acts_dict.append(act_dict)

    r = session.restclient.completarActividades(acts_dict, resultado, justification)

    return r
