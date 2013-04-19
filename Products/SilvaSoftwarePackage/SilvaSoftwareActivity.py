
import operator
import json
import feedparser
import datetime

from persistent import Persistent

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from BTrees.IOBTree import IOBTree
from OFS.SimpleItem import SimpleItem
from Products.Silva import SilvaPermissions
from Products.Silva.Content import Content
from five import grok
from zope import schema
from zope.component import getUtility
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.intid.interfaces import IIntIds
from Products.SilvaExternalSources.ExternalSource import ExternalSource

from js.jquery import jquery
from silva.core.services.interfaces import ICatalogService
from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews
from silva.core.conf.interfaces import ITitledContent
from silva.fanstatic import need
from zeam.form import silva as silvaforms
from silva.core.contentlayout.interfaces import IBlockable
from silva.core.contentlayout.blocks import BlockView


class IGraphResources(IDefaultBrowserLayer):
    silvaconf.resource(jquery)
    silvaconf.resource('RGraph.common.core.js')
    silvaconf.resource('RGraph.line.js')
    silvaconf.resource('activity.js')


class Change(object):

    def __init__(self, uid, author, date, message):
        self.uid = uid
        self.date = date
        self.message = message
        self.author = author

class Changes(Persistent):

    def __init__(self):
        self._changes = []
        self._known = set([])

    def add(self, change):
        if change.uid not in self._known:
            self._known.add(change.uid)
            self._changes.append(change)
            self._p_changed = True
            return True
        return False

    def __len__(self):
        return len(self._changes)

    def __iter__(self):
        return iter(self._changes)


class SilvaSoftwareActivity(Content, SimpleItem, ExternalSource):
    """Collect activity from an RSS feed and generate statistics about
    it.
    """
    grok.implements(IBlockable)
    meta_type = 'Silva Software Activity'
    security = ClassSecurityInfo()

    _rss_url = None
    _data = None

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_rss_url')
    def get_rss_url(self):
        return self._rss_url

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_rss_url')
    def set_rss_url(self, url):
        self._rss_url = url

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_changes_since')
    def get_changes_since(self, days=31, empty=True):
        """Return the changes since the given number of days.
        """
        if self._data is not None:
            today = datetime.date.today()
            today_day = today.toordinal()
            since = (today - datetime.timedelta(days))
            since_day = since.toordinal()
            if not empty:
                return list(self._data.values(since_day))
            data = self._data.items(since_day)
            result = []
            for day, values in data:
                while day > since_day:
                    result.append([])
                    since += datetime.timedelta(1)
                    since_day = since.toordinal()
                result.append(values)
                since += datetime.timedelta(1)
                since_day = since.toordinal()
            if result:
                while today_day > since_day:
                    result.append([])
                    since += datetime.timedelta(1)
                    since_day = since.toordinal()
            return result
        return []

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'refresh')
    def refresh(self):
        """Refresh the data stored.
        """
        rss_url = self.get_rss_url()
        if rss_url is None:
            return
        if self._data is None:
            self._data = IOBTree()
        data = feedparser.parse(rss_url)
        changed = False
        for entry in data['entries']:
            date = datetime.date(*entry['updated_parsed'][:3])
            key = date.toordinal()
            if key not in self._data:
                self._data[key] = Changes()
            change = Change(
                    entry['id'],
                    entry['author'],
                    date,
                    entry['summary'])
            changed = self._data[key].add(change) or changed
        if changed:
            self._p_changed = True

    def is_previewable(self):
        return False

    def to_html(self, content, request, **parameters):
        return silvaviews.render(self, request)


InitializeClass(SilvaSoftwareActivity)


class IActivityFields(ITitledContent):
    rss_url = schema.URI(
        title=u'RSS URL',
        description=u'URL tracking changes')

def rss_url_default_value(form):
    package_name = form.context.get_container().getId()
    if '.' not in package_name:
        package_name = 'products.' + package_name.lower()
    else:
        package_name = package_name.lower()
    return 'http://dev.infrae.com/log/{0}/?format=rss'.format(
        package_name)

def title_default_value(form):
    return form.context.get_container().get_title()

def id_default_value(form):
    return 'activity'


ActivityFields = silvaforms.Fields(IActivityFields)
ActivityFields['id'].defaultValue = id_default_value
ActivityFields['title'].defaultValue = title_default_value
ActivityFields['rss_url'].defaultValue = rss_url_default_value


class ActivityAddForm(silvaforms.SMIAddForm):
    grok.name('Silva Software Activity')
    grok.context(SilvaSoftwareActivity)

    fields = ActivityFields


class ActivityEditForm(silvaforms.SMIEditForm):
    grok.context(SilvaSoftwareActivity)

    actions = silvaforms.SMIEditForm.actions.copy()
    fields = ActivityFields.omit('id')

    @silvaforms.action('Refresh')
    def refresh(self):
        self.context.refresh()


class ActivityRender(silvaviews.Render):
    grok.context(SilvaSoftwareActivity)

    days = 31

    def update(self):
        need(IGraphResources)
        self.changes  = self.context.get_changes_since(self.days)
        self.values = json.dumps([len(a) for a in self.changes])


class ActivityView(silvaviews.View):
    grok.context(SilvaSoftwareActivity)

    def update(self):
        self.info = silvaviews.render(self.context, self.request)


class ActivityBlock(BlockView):
    grok.context(SilvaSoftwareActivity)

    def render(self):
        return silvaviews.render(self.context, self.request)


class SilvaSoftwareActivityAggregator(Content, SimpleItem, ExternalSource):
    """Aggregate multiple activities together.
    """
    grok.implements(IBlockable)
    meta_type = 'Silva Software Activity Aggregator'
    security = ClassSecurityInfo()

    _data = None
    _most_actives = []

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_changes_since')
    def get_changes_since(self, days=31, empty=True):
        """Return the changes since the given number of days.
        """
        if self._data is not None:
            today = datetime.date.today()
            today_day = today.toordinal()
            since = (today - datetime.timedelta(days))
            since_day = since.toordinal()
            if not empty:
                return list(self._data.values(since_day))
            data = self._data.items(since_day)
            result = []
            for day, values in data:
                while day > since_day:
                    result.append([])
                    since += datetime.timedelta(1)
                    since_day = since.toordinal()
                result.append(values)
                since += datetime.timedelta(1)
                since_day = since.toordinal()
            if result:
                while today_day > since_day:
                    result.append([])
                    since += datetime.timedelta(1)
                    since_day = since.toordinal()
            return result
        return []

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'refresh')
    def refresh(self):
        """Refresh the data stored.
        """
        if self._data is None:
            self._data = IOBTree()

        counts = {}
        catalog = getUtility(ICatalogService)
        for brain in catalog(
            meta_type=['Silva Software Activity'],
            path='/'.join(self.get_container().getPhysicalPath())):
            activity = brain.getObject()
            counts[brain.content_intid] = 0
            changes = activity.get_changes_since(empty=False)
            print activity.get_title(), len(changes)
            for change in changes:
                for commit in change:
                    key = commit.date.toordinal()
                    if key not in self._data:
                        self._data[key] = Changes()
                    self._data[key].add(commit)
                counts[brain.content_intid] += len(change)
        self._most_actives = map(
            operator.itemgetter(0),
            sorted(counts.items(), key=operator.itemgetter(1), reverse=True))

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_most_active')
    def get_most_active(self, limit=5):
        get_activity = getUtility(IIntIds).getObject
        return map(lambda i: get_activity(i).get_container(),
                   self._most_actives[:limit])

    def is_previewable(self):
        return False

    def to_html(self, content, request, **parameters):
        return silvaviews.render(self, request)



InitializeClass(SilvaSoftwareActivityAggregator)


class ActivityAggregatorAddForm(silvaforms.SMIAddForm):
    grok.name('Silva Software Activity Aggregator')
    grok.context(SilvaSoftwareActivityAggregator)

    fields = silvaforms.Fields(ITitledContent)
    fields['id'].defaultValue = id_default_value
    fields['title'].defaultValue = title_default_value


class ActivityAggregatorEditForm(silvaforms.SMIEditForm):
    grok.context(SilvaSoftwareActivityAggregator)

    actions = silvaforms.SMIEditForm.actions.copy()
    fields = silvaforms.Fields(ITitledContent).omit('id')

    @silvaforms.action('Refresh')
    def refresh(self):
        self.context.refresh()


class ActivityAggregatorRender(silvaviews.Render):
    grok.context(SilvaSoftwareActivityAggregator)

    days = 31
    include_changes = True
    include_actives = True

    def update(self):
        self.actives = []
        self.changes = []
        if self.include_changes:
            need(IGraphResources)
            self.changes  = self.context.get_changes_since(self.days)
            self.values = json.dumps([len(a) for a in self.changes])
        if self.include_actives:
            self.actives = self.context.get_most_active()


class ActivityAggregatorView(silvaviews.View):
    grok.context(SilvaSoftwareActivityAggregator)

    def update(self):
        self.info = silvaviews.render(self.context, self.request)


class ActivityAggregatorBlock(BlockView):
    grok.context(SilvaSoftwareActivityAggregator)

    def render(self):
        return silvaviews.render(self.context, self.request)
