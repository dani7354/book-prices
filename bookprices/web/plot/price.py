import base64
from io import BytesIO
from matplotlib.figure import Figure
from dataclasses import dataclass


@dataclass(frozen=True)
class LineData:
    title: str
    dates: list[str]
    prices: list[float]


class PriceHistory:
    PLOT_STYLE = "seaborn-dark"
    IMAGE_FORMAT = "png"

    def __init__(self, lines: list[LineData]):
        self._lines = lines

    def _plot(self) -> bytes:
        figure = Figure(figsize=(10, 5))
        subplot = figure.subplots()
        for line in self._lines:
            subplot.plot(line.dates, line.prices, "-o", label=line.title)

        subplot.tick_params(axis='x', rotation=90)
        subplot.legend()
        subplot.set_xlabel("Dato")
        subplot.set_ylabel("Pris")
        figure.align_labels()

        img_buf = BytesIO()
        figure.savefig(img_buf, format=self.IMAGE_FORMAT, dpi=100, bbox_inches="tight")

        return img_buf.getvalue()

    def get_plot_base64(self) -> str:
        plot_bytes = self._plot()

        return base64.b64encode(plot_bytes).decode("ascii")
