import json
import logging
from time import sleep
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
import subprocess

logger = logging.getLogger(__name__)


class DemoExtension(Extension):

    def __init__(self):
        super(DemoExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []

        logger.info('preferences %s' % json.dumps(extension.preferences))

        setting_path = extension.preferences['setting_path']
        setting_limit = extension.preferences['setting_limit']

        out = subprocess.Popen([setting_path, '--export', 'json', '-n', setting_limit],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)

        stdout,stderr = out.communicate()

        a = json.loads(stdout)

        query = event.get_argument() or ""
        split_query = query.partition(" ")

        keyword = split_query[0]

        if keyword != "":



            items.append(ExtensionResultItem(icon='images/jrnl_white.svg',
                                            name="Press enter to add: %s" % (query),
                                            highlightable=False,
                                            on_enter=ExtensionCustomAction(query, keep_app_open=True)))

            return RenderResultListAction(items)

        else:
            for i in a['entries']:
                item_title = i['title']
                item_body = i['body']
                item_date = i['date']
                item_starred = i['starred']

                items.append(ExtensionResultItem(icon='images/jrnl_white.svg',
                                                 name='%s' % item_title,
                                                 description='%s\n%s\nStarred: %s' % (item_body, item_date, item_starred),
                                                 highlightable=False,
                                                 on_enter=DoNothingAction()
                                                 )
                            )

            return RenderResultListAction(items)

class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):

        items = []

        data = event.get_data()

        print(data)

        out = subprocess.Popen(['jrnl', data],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

        stdout,stderr = out.communicate()

        rc = out.returncode

        if rc == 0:
            items.append(ExtensionResultItem(icon='images/jrnl_white.svg',
                                                            name="Added %s to your journal" % data,
                                                            highlightable=False,
                                                            on_enter=HideWindowAction()))
            return RenderResultListAction(items)
        else:
            items.append(ExtensionResultItem(icon='images/jrnl_white.svg',
                                                            name="Error",
                                                            highlightable=False,
                                                            on_enter=HideWindowAction()))
        return RenderResultListAction(items)



if __name__ == '__main__':
    DemoExtension().run()
