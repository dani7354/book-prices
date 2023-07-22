import base64
from io import BytesIO
from matplotlib.figure import Figure


class PriceHistory:
    PLOT_STYLE = 'seaborn-dark'
    IMAGE_FORMAT = 'png'

    def __init__(self, prices_by_date: dict, title: str):
        self._prices_by_date = prices_by_date
        self._title = title

    def _plot(self) -> bytes:
        figure = Figure(figsize=(10, 5))
        subplot = figure.subplots()
        subplot.plot(self._prices_by_date.keys(), self._prices_by_date.values(), "o-r")

        subplot.tick_params(axis='x', rotation=90)
        subplot.set_xticks(list(self._prices_by_date.keys()))
        subplot.legend()

        subplot.set_xlabel("Dato")
        subplot.set_ylabel("Pris")
        figure.align_labels()

        img_buf = BytesIO()
        figure.savefig(img_buf, format=self.IMAGE_FORMAT, dpi=100, bbox_inches='tight')

        return img_buf.getvalue()

    def get_plot_base64(self) -> str:
        plot_bytes = self._plot()

        return base64.b64encode(plot_bytes).decode("ascii")
