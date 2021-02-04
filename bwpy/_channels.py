class Channel:
    def __init__(self, bxr, row, col):
        self._bxr = bxr
        self._row = row
        self._col = col

    @classmethod
    def _from_bxr_list(cls, bxr, bxr_list):
        return [cls._from_bxr(bxr, data) for data in bxr_list]

    @classmethod
    def _from_bxr(cls, bxr, bxr_data):
        return cls(bxr, bxr_data[0], bxr_data[1])


class ChannelGroup:
    def __init__(self, name, channels, color=None, visible=True):
        self._name = name
        self._channels = channels
        self._color = color
        self._visible = visible

    @property
    def name(self):
        return self._name

    @property
    def channels(self):
        return self._channels.copy()

    @property
    def color(self):
        return self._color

    @property
    def visible(self):
        return self._visible

    @classmethod
    def _from_bxr(cls, bxr, bxr_data):
        channels = Channel._from_bxr_list(bxr, bxr_data["Chs"])
        return cls(
            bxr_data["Name"], channels, bxr_data["Color"], bool(bxr_data["IsVisible"])
        )
