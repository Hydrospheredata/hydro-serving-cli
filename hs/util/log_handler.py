import logging
import click

class StdoutLogHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            click.echo(msg)
        except Exception:
            self.handleError(record)