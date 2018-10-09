import luis as msluis
url = "https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/9f0dd57a-bd9b-48dd-97c9-bea0c9b85ee6?subscription-key=77b349a96e6b4c0ea734e76cdf4dfd0d&verbose=true&timezoneOffset=0&q="
luis = msluis.Luis(url=url)

routes = {
    'reset-password': '/api/reset-password/begin'
}

entity_list = {
    'reset-password': ['portal_id', 'postal_code', 'phone_number', 'city']
}

'''
def getRoute(text):
    result = luis.analyze(text).best_intent()
    intent = result.intent
    entities = luis.analyze(data).entities

    route  = routes.get(intent, None)
    return route
'''

def getRoute(text):
    result = luis.analyze(text)
    intent = result.best_intent().intent
    entites = result.entities
    entites = extractEntities(entites, entity_list.get(intent,None))
    return routes.get(intent, None), entites 


def extractEntities(entities, keys):
    if not entities or not keys:
        return None
    
    rel_entities = list(filter( lambda x : x.type in keys, entities))
    return { 'luis_'+x.type: get_entity_val(x) for x in rel_entities }


def get_entity_val(entity):
    if entity.resolution:
        vals = entity.resolution.get('value') or entity.resolution.get('values')
        if (type(vals) == list):
            return vals[0]
        else:
            return vals
    else:
        return entity.entity