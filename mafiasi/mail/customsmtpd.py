import asyncio
import logging

from aiosmtpd.controller import Controller

logger = logging.getLogger(__name__)


class RaisingHandler:
    """Base class: subclasses implement the old-style process_message()."""

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        raise NotImplementedError

    async def handle_DATA(self, server, session, envelope):
        result = await asyncio.to_thread(
            self.process_message,
            session.peer,
            envelope.mail_from,
            envelope.rcpt_tos,
            envelope.content,
        )
        return result or "250 OK"

    async def handle_exception(self, error):
        logger.exception("Unhandled error while processing mail", exc_info=error)
        return "451 Requested action aborted: error in processing"


def start_server(handler, host, port):
    controller = Controller(handler, hostname=host, port=port)
    controller.start()
    return controller


def _run(self, *args):
    try:
        return self.process_message(*args)
    finally:
        connection.close()


async def handle_DATA(self, server, session, envelope):
    result = await asyncio.to_thread(
        self._run,
        session.peer,
        envelope.mail_from,
        envelope.rcpt_tos,
        envelope.content,
    )
    return result or "250 OK"
