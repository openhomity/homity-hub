"""Base object corresponding to CouchDB entries."""
import inspect

from couchdb.mapping import Document
from Hub.api import couch
from sys import modules

from Hub.v1.Common.db_helpers import get_couch_db

class HomityObject(Document):
    """Base class for Homity object.  Builtins for get/find/save."""
    def __init__(self, id=None, **values):
        Document.__init__(self, id, **values)
        self.class_db = get_couch_db(type(self).__name__)
        self.refresh()
        self.save()

    @classmethod
    def get_id(cls, spoke_id):
        """Get a specific document from the database.

        :param id: the document ID
        :return: the `Document` instance, or `None` if no document with the
                 given ID was found
        """
        class_db = get_couch_db(cls.__name__)

        doc = class_db.get(spoke_id)
        if doc is None:
            return None
        return cls.wrap(doc)

    @classmethod
    def _list(cls, dict_format=False):
        """Return list of objects of type."""
        class_db = get_couch_db(cls.__name__)
        object_list = []
        for class_entry in class_db:
            class_object = cls.load(class_db,
                               class_entry)
            if dict_format:
                object_list.append(class_object.dict())
            else:
                object_list.append(class_object)
        return object_list

    @classmethod
    def _find(cls, **kwargs):
        """Return object of class type that matches kwargs filters."""
        #untested
        matches = cls._find_all(dict_format, **kwargs)
        num_matches = len(matches)
        if num_matches == 0:
            msg = "No %s matching %s." % (cls.__name__, kwargs)
            return False, msg
        elif num_matches > 1:
            msg = ("Too many matches %s for %s matching %s." %
                   (str(num_matches), cls.__name__, kwargs))
            return False, msg
        else:
            return True, matches[0]

    @classmethod
    def _find_all(cls, **kwargs):
        """Return all objects of class type that match kwargs filters."""
        #untested
        found = []

        listing = cls._list()
        searches = kwargs.items()
        for obj in listing:
            try:
                if all(getattr(obj, attr) == value
                        for (attr, value) in searches):
                    found.append(obj)
            except AttributeError:
                continue

        return found

    @classmethod
    def _find_in_list(cls, **kwargs):
        """Return object of class type where value is in list(key)."""
        #untested
        matches = cls._find_all_in_list(**kwargs)
        num_matches = len(matches)
        if num_matches == 0:
            msg = "No %s matching %s." % (cls.__name__, kwargs)
            return False, msg
        elif num_matches > 1:
            msg = ("Too many matches %s for %s matching %s." %
                   (str(num_matches), cls.__name__, kwargs))
            return False, msg
        else:
            return True, matches[0]

    @classmethod
    def _find_all_in_list(cls, **kwargs):
        """Return all objects of class type where value is in list(key)."""
        #untested
        found = []

        listing = cls._list()
        searches = kwargs.items()
        for obj in listing:
            try:
                if all(value in list(obj.attr)
                        for (attr, value) in searches):
                    found.append(obj)
            except AttributeError:
                continue

        return found

    def save(self):
        """Save current self."""
        return self.store(self.class_db)

    def refresh(self):
        """Override with class-specific refresh."""
        pass

    def delete(self):
        """Grab all non-built-in attributes."""
        del self.class_db[self.id]

    def dict(self):
        """Return object in dictionary form."""
        return dict([(k, v) for k, v in self._data.items()
                                        if k not in ('_id', '_rev')])




