import smtpd


class RaisingSMTPChannel(smtpd.SMTPChannel):
    def handle_error(self):
        raise


class RaisingSMTPServer(smtpd.SMTPServer):
    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            conn, addr = pair
            RaisingSMTPChannel(self, conn, addr)
