from .signal import *
import abc
import plotly.graph_objects as go
import numpy as np


class Viewer(abc.ABC):
    @abc.abstractmethod
    def set_up_view(self, slice, bin_size, view_method):
        pass


class MEAViewer(Viewer):
    colorscale = [[0, "#ebe834"], [1.0, "#eb4034"]]
    min_value = 0
    max_value = 170

    def set_up_view(self, slice, view_method, bin_size=100):
        sliced_data = slice.data
        fig = go.Figure()
        for i in range(0, sliced_data.shape[1]):
            if sliced_data.shape[1] - i < bin:
                break
            transform = getattr(signal, view_method)
            bin = self.ms_to_idx(slice, bin_size)
            signal = transform(slice._file.t[i : i + bin]).data
            fig.add_trace(
                go.Heatmap(
                    visible=False,
                    z=signal,
                    zmin=self.min_value,
                    zmax=self.max_value,
                    colorscale=self.colorscale,
                )
            )
        return fig

    def ms_to_idx(self, slice, bin_size):
        return slice._file.n_frames * slice._file.sampling_rate, bin_size

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
