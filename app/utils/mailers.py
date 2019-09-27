# -*- coding:utf-8 -*-

import os, mimetypes, json, markdown, logging, sys, base64, config
from app.utils.frequests import Frequests

mimetypes.init()


def get_mailer(name=None):
    if name is None:
        name = config.MAILER_SERVICE

    thismodule = sys.modules[__name__]
    return getattr(thismodule, name)


def guess_mimetype(name):
    type_found = mimetypes.guess_type(name)
    if type_found:
        return type_found[0]  # Best guess

    return 'text/plain'

class Sendgrid(object):
    def __init__(self, subject, template=None, text=None, html=None):
        self.data = {
            'personalizations': [],
            'subject': subject,
            'content': [],
            'headers': {
                'X-Myapp-Version': 'v1'
            },
            'tracking_settings': {
                'click_tracking': {
                    'enable': True,
                    'enable_text': False
                },
                'open_tracking': {
                    'enable': True
                }
            }
        }

        self.set_from(config.CONTACT_NAME, config.CONTACT_EMAIL)

        html_body = None
        text_body = None

        if template:
            # set html and text
            path = os.path.join(config.APPLICATION_PATH, 'templates', 'emails')

            try:
                txt_file = open(os.path.join(path, '{0}.txt'.format(template)))
                text_body = txt_file.read()
                txt_file.close()
            except IOError:
                pass

            try:
                html_file = open(os.path.join(path, '{0}.html'.format(template)))
                html_body = html_file.read()
                html_file.close()
            except IOError:
                pass

        if text:
            text_body = text

        if html:
            html_body = html

        if text_body is None and html_body is None:
            raise ValueError('Unable to find the specified template.')

        if text_body and html_body is None:
            html_body = markdown.markdown(text_body)

        if text_body is not None:
            self.data['content'].append({
                'type': 'text/plain',
                'value': text_body
            })

        if html_body is not None:
            self.data['content'].append({
                'type': 'text/html',
                'value': html_body
            })

    def set_from(self, from_name, from_email):
        self.data['from'] = {
            'name': from_name,
            'email': from_email
        }

        self.data['reply_to'] = self.data['from']

    def _add(self, kind, name, content, mimetype=None):
        if not mimetype:
            mimetype = guess_mimetype(name)

        if 'attachments' not in self.data:
            self.data['attachments'] = []

        self.data['attachments'].append({
            'type': mimetype,
            'filename': name,
            'content': base64.b64encode(content),  # content.encode('base64').decode('utf-8').replace('\n', ''),
            'disposition': kind
        })

    def add_attachment(self, name, content, type=None):
        self._add('attachment', name, content, type)

    def add_inline(self, name, content, type=None):
        self._add('inline', name, content, type)

    def queue(self, name, email, substitution=None):
        target_email = {
            'to': [{
                'name': name,
                'email': email
            }],
            'subject': self.data['subject']
        }

        if substitution is not None:
            updated_substitution = {}
            for key in substitution:
                updated_substitution['{{{{{0}}}}}'.format(key)] = str(substitution[key])

            target_email['substitutions'] = updated_substitution

        self.data['personalizations'].append(target_email)

    def send_to(self, name, email, substitution=None, send_at=None):
        self.data['personalizations'] = []
        self.queue(name, email, substitution)

        result = self.send(send_at)

        logging.info('Sent email to {0} with subject {1} with result {2}'.format(email, self.data.get('subject', None), json.dumps(result)))

    def send(self, send_at=None):
        if send_at:
            self.data['send_at'] = send_at.replace(microsecond=0).isoformat()

        try:
            r = Frequests.post(
                'https://api.sendgrid.com/v3/mail/send',
                timeout=10,
                headers={'Authorization': 'Bearer {0}'.format(config.SENDGRID_API_KEY)},
                json=self.data
            )

            if r.status_code < 300:
                return r.json()
            else:
                logging.error(r.content)
        except Exception:
            logging.exception("[SendGrid]")

        return None
