import logging
import click
import click_log
import json

class StdoutLogHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            click.echo(msg)
        except Exception:
            self.handleError(record)


class PrettyFormatter(click_log.ColorFormatter):
    def __init__(self, pretty_print: bool):
        super().__init__()
        self.pretty_print = pretty_print

    def format(self, record):
        record = super().format(record)
        if self.pretty_print:
            try:
                return json.dumps(json.loads(record), indent=4)
            except json.JSONDecodeError:
                pass
        return record