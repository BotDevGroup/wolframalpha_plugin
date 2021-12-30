# -*- coding: utf-8 -*-
from marvinbot.handlers import CommandHandler
from marvinbot.plugins import Plugin
import logging
import wolframalpha
import html

log = logging.getLogger(__name__)


class WolframAlphaPlugin(Plugin):
    def __init__(self):
        super(WolframAlphaPlugin, self).__init__('wolframalpha_plugin')
        self.client = None
        self.config = None

    def get_default_config(self):
        return {
            'short_name': self.name,
            'enabled': True,
            'app_id': None,
        }

    def configure(self, config):
        if config.get('app_id') is None:
            log.warn('No app_id set')
        self.client = wolframalpha.Client(config.get('app_id'))

    def setup_handlers(self, adapter):
        # TODO: Add --show-images argument
        self.add_handler(CommandHandler('wa', self.on_query, command_description='Allows the user to query WolframAlpha knowledge engine.')
                         .add_argument('--verbose', help='Get a more detailed response', action='store_true')
                         .add_argument('query', nargs='*', help='Query (e.g. 2+2)'))

    def setup_schedules(self, adapter):
        pass

    def on_query(self, update, *args, **kwargs):
        query = ' '.join(kwargs.get('query'))
        verbose = kwargs.get('verbose')

        def escape_html(text):
            return html.escape(text)

        try:
            query_response = self.client.query(query)
            if verbose:
                response = "\n\n".join(["<b>{}</b>: {}".format(result.title, escape_html(result.text)) for result in query_response.pods if result.text is not None])
            else:
                response = "\n\n".join(["<b>{}</b>: {}".format(result.title, escape_html(result.text)) for result in query_response.results])
            if response:
                update.effective_message.reply_text(response, parse_mode='HTML')
            else:
                update.effective_message.reply_text("❌ No results.")
        except Exception as ex:
            log.error(ex)
            update.effective_message.reply_text("❌ Invalid query: {}".format(query))
