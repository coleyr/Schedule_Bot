import json

def _filter_dict(dict_to_parse: dict, message_params: str):
    """
    filters out keywords based on message contents
    :param dictionary to parse
    :param incoming_msg: The incoming message object from Teams
    :return: A dictionary""" 

    message_keywords = [item.lower() for item in message_params.split()]
    new_dict = {key: dict_to_parse[key]
                for key in dict_to_parse
                if key.lower() in message_keywords}
    if not new_dict:
        return dict_to_parse
    return new_dict
    
def _format_time(time: dict, message_params: str):
    time_template = """{time} : {en1} and {en2}\n"""
    time_out = ""
    time = _filter_dict(time, message_params) if message_params else time
    for t, engineers in time.items():
        en1 = engineers[0] if 0 <= 0 < len(
            engineers) else "No Engineer Assigned"
        en2 = engineers[1] if 0 <= 1 < len(
            engineers) else "No Engineer Assigned"
        time_out += time_template.format(time=t, en1=en1, en2=en2)
    return time_out


def _format_tier(tier: dict, message_params: str):
    # Todo intake message params filter for tier
    tier = _filter_dict(tier, message_params) if message_params else tier
    tier_tempplate = '''The following {tier} engineers are assinged to work:\n'''
    return "".join(
       (tier_tempplate.format(tier=tier.upper()) + _format_time(time, message_params))
        for tier, time in tier.items()
    )


def _format_schedule_msg(sc: dict, message_params: str):
    template = """\
        On date: {date}
        """
    out = ""
    sc = _filter_dict(sc, message_params) if message_params else sc
    # Todo intake message params filter for date
    for date, tier in sc.items():
        out += template.format(date=date)
        out += _format_tier(tier, message_params)

    return out

# A simple command that returns weeks schedule


def show_schedule(incoming_msg):
    """
    Sample function to do some action.
    :param incoming_msg: The incoming message object from Teams
    :return: A text or markdown based reply
    """
    message_params = bot.extract_message(
        "/schedule", incoming_msg.text).strip()

    with open('sample_data.json', 'r') as f:
        sc = json.loads((f.read()))
    return _format_schedule_msg(sc, message_params=message_params)