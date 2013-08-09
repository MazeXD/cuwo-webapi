import json


def generate_error(error_code, request=None):
    result = {
        'response': 'error',
        'data': error_code
    }
    if isinstance(request, basestring):
        result['request'] = request
    return json.dumps(result)


def generate_success(request, data=None):
    result = {
        'response': 'success'
    }
    if data is not None:
        result['data'] = data
    if isinstance(request, basestring):
        result['request'] = request
    return json.dumps(result)


def generate_update(request, data=None):
    result = {
        'response': 'update'
    }
    if data is not None:
        result['data'] = data
    if isinstance(request, basestring):
        result['request'] = request.lower()
    return json.dumps(result)


def log(message):
    print '[WebAPI] %s' % message


def fullname(klass):
    module = klass.__module__
    if not module:
        return klass.__name__
    return module + "." + klass.__name__


# Thanks to Sarcen for the formula
def get_power_level(level):
    power = 101 - 100 / (0.05 * (level - 1) + 1)
    return int(power)


def encode_item_upgrade(upgrade):
    encoded = {
        'x': upgrade.x,
        'y': upgrade.y,
        'z': upgrade.z,
        'material': upgrade.material,
        'level': upgrade.level
    }
    return encoded


def encode_item(item):
    encoded = {
        'type': item.type,
        'sub-type': item.sub_type,
        'modifier': item.modifier,
        'minus-modifier': item.minus_modifier,
        'rarity': item.rarity,
        'material': item.material,
        'flags': item.flags,
        'level': item.level,
        'power-level': get_power_level(item.level),
        'upgrades': [encode_item_upgrade(item.items[i])
                     for i in xrange(item.upgrade_count)]
    }
    return encoded


def encode_player(connection, detailed=False):
    player = connection.entity_data
    encoded = {
        'name': player.name,
        'level': player.level,
        'power-level': get_power_level(player.level),
        'class': player.class_type,
        'specialization': player.specialization
    }
    if detailed:
        skills = {
            'pet-master': player.skills[0],
            'riding': player.skills[1],
            'climbing': player.skills[2],
            'hang-gliding': player.skills[3],
            'swimming': player.skills[4],
            'sailing': player.skills[5],
            'class-skill-1': player.skills[6],
            'class-skill-2': player.skills[7],
            'class-skill-3': player.skills[8]
        }
        encoded['skills'] = skills
        encoded['items'] = [encode_item(item) for item in player.equipment]
    encoded['entity-id'] = connection.entity_id
    encoded['ip'] = connection.address.host
    return encoded
