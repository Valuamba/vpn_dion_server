from wireguard.models import WgInfo


def create_wg_info(key_value_pairs) -> WgInfo:
    wg_info = WgInfo()
    for pair in key_value_pairs:
        setattr(wg_info, pair['key'].replace(' ', '_'), pair['value'])
    return wg_info