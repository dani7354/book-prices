import base64
import io
import matplotlib.pyplot as pyplot


class PriceHistory:
    PLOT_STYLE = 'seaborn-dark'
    IMAGE_FORMAT = 'png'

    def __init__(self, dates: list, prices: list, title: str):
        self._dates = dates
        self._prices = prices
        self._title = title

    def _plot(self) -> bytes:
        pyplot.style.use(self.PLOT_STYLE)
        pyplot.plot(self._dates, self._prices)
        pyplot.xlabel("Dato")
        pyplot.ylabel("Pris")
        pyplot.title(self._title)
        pyplot.legend()
        plot_image = io.BytesIO()
        pyplot.savefig(plot_image, format=self.IMAGE_FORMAT)

        return plot_image.getvalue()

    def get_plot_base64(self) -> str:
        plot_bytes = self._plot()

        return base64.b64encode(plot_bytes).decode()
