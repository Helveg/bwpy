from . import signal
import abc
import plotly.graph_objects as go
import numpy as np
from scipy.stats import norm


class Viewer(abc.ABC):
    @abc.abstractmethod
    def build_view(self, slice, bin_size, view_method):
        pass


class MEAViewer(Viewer):
    colorscale = [[0, "#ebe834"], [1.0, "#eb4034"]]
    min_value = 0
    max_value = 0

    def build_view(
        self, file, slice=None, view_method="amplitude", bin_size=100, data=None
    ):
        fig = go.Figure()
        if slice and data:
            raise ValueError("slice and data arguments are mutually exclusives.")
        if slice:
            apply_transformation = getattr(signal, view_method)
            signals = apply_transformation(slice, bin_size).data
        else:
            signals = data

        for signal_frame in signals:
            fig.add_trace(
                go.Heatmap(
                    visible=False,
                    z=signal_frame,
                    zmin=self.min_value,
                    zmax=self.get_up_bound(signals, file),
                    colorscale=self.colorscale,
                )
            )
        return self.format_plot(fig)

    def ms_to_idx(self, slice, bin_size):
        return slice._file.n_frames / slice._file.sampling_rate, bin_size

    def get_up_bound(self, data, file):
        up_limit = file.convert(file.max_volt) * 0.98
        no_artifacts = data[data < up_limit]
        mu, sd = norm.fit(no_artifacts.reshape(-1))
        return mu + 2 * sd

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
