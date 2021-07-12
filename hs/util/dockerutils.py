from typing import Dict, Optional
import click

class DockerLogHandler:
    prev_msg: Optional[str] = None
    first_line: bool = True

    def show(self, msg: str):
        if self.prev_msg != msg:
            if self.first_line:
                self.first_line = False
            else:
                click.echo()
            click.echo(msg, nl=False)
        else:
            click.echo(".", nl=False)
        self.prev_msg = msg