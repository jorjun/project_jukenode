from www.jukenode.nosql import Collection, GridFile, get_db


__all__ = ['NOD', 'AUD']

class __JukeBase(Collection):
    db = get_db('juke_network')


class AudioFS(GridFile):
    db = get_db('juke_audio')

AUD = AudioFS()

class JukeNode(__JukeBase):
    """
    node_name : nnn
    node_description : nnn
    node_type : '1' = Speaker, '2' = Microphone
    node_ip: ip_address,
    node_beat_interval: nnn,
    """
    col_name = 'node'
    pk_fields = ('node_name', )


NOD = JukeNode()