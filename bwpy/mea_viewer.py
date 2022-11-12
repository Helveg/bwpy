from . import signal
import abc
import plotly.graph_objects as go
import numpy as np


class Viewer(abc.ABC):
    @abc.abstractmethod
    def build_view(self, slice, bin_size, view_method):
        pass


class MEAViewer(Viewer):
    colorscale = [[0, "#ebe834"], [1.0, "#eb4034"]]
    min_value = 0
    max_value = 0

    def build_view(self, slice, view_method="amplitude", bin_size=100):
        self.min_value = slice._file.convert(slice._file.min_volt)
        self.max_value = slice._file.convert(slice._file.max_volt)
        # min = -12433, max = 4183
        self.min_value = 0
        self.max_value = 170
        fig = go.Figure()
        apply_transformation = getattr(signal, view_method)
        signals = apply_transformation(slice, bin_size).data
        for signal_frame in signals:
            fig.add_trace(
                go.Heatmap(
                    visible=False,
                    z=signal_frame,
                    zmin=self.min_value,
                    zmax=self.max_value,
                    colorscale=self.colorscale,
                )
            )
        return fig

    def ms_to_idx(self, slice, bin_size):
        return slice._file.n_frames / slice._file.sampling_rate, bin_size

    def format_plot(self, fig):
        # Create and add slider
        fig.data[0].visible = True
        steps = []
        for i in range(len(fig.data)):
            step = dict(
                method="update",
                args=[
                    {"visible": [False] * len(fig.data)},
                    {"title": "Time slice: " + str(i)},
                ],  # layout attribute
            )
            step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
            steps.append(step)

        sliders = [
            dict(active=0, currentvalue={"prefix": "Time: "}, pad={"t": 50}, steps=steps)
        ]

        fig.update_layout(
            yaxis=dict(scaleanchor="x", autorange="reversed"), sliders=sliders
        )
        return fig

    def show(self, fig):
        fig.show()
