# -*- coding: utf-8 -*-
# Caliper-python package, base module
#
# This file is part of the IMS Caliper Analytics(tm) and is licensed to IMS
# Global Learning Consortium, Inc. (http://www.imsglobal.org) under one or more
# contributor license agreements. See the NOTICE file distributed with this
# work for additional information.
#
# IMS Caliper is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, version 3 of the License.
#
# IMS Caliper is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#


import collections
import copy
import json
from rfc3987 import parse as rfc3987_parse
import six


### Default configuration values ###

class Options(object):
    _config = {
        'API_KEY': None,
        'HOST' : None,
        'CONNECTION_TIMEOUT': None,
        'SO_TIMEOUT': None,
        'CONNECTION_REQUEST_TIMEOUT': None,
        }

    def __init__(self):
        pass

    @property
    def API_KEY(self):
        return self._config['API_KEY']
    @API_KEY.setter
    def API_KEY(self, new_key):
        if isinstance(new_key, six.string_types):
            self._config['API_KEY'] = str(new_key)
        else:
            raise ValueError('new key value must be a string')
        
    @property
    def HOST(self):
        return self._config['HOST']
    @HOST.setter
    def HOST(self,new_host):
        if rfc3987_parse(new_host, rule='URI'):
            self._config['HOST'] = str(new_host)

    @property
    def CONNECTION_TIMEOUT(self):
        return self._config['CONNECTION_TIMEOUT']
    @CONNECTION_TIMEOUT.setter
    def CONNECTION_TIMEOUT(self, new_timeout):
        if int(new_timeout) >= 1000:
            self._config['CONNECTION_TIMEOUT'] = int(new_timeout)
        else:
            raise ValueError('new timeout value must be at least 1000 milliseconds')

    @property
    def SO_TIMEOUT(self):
        return self._config['SO_TIMEOUT']
    @SO_TIMEOUT.setter
    def SO_TIMEOUT(self, new_timeout):
        if int(new_timeout) >= 1000:
            self._config['SO_TIMEOUT'] = int(new_timeout)
        else:
            raise ValueError('new timeout value must be at least 1000 milliseconds')

    @property
    def CONNECTION_REQUEST_TIMEOUT(self):
        return self._config['CONNECTION_REQUEST_TIMEOUT']
    @CONNECTION_REQUEST_TIMEOUT.setter
    def CONNECTION_REQUEST_TIMEOUT(self, new_timeout):
        if int(new_timeout) >= 1000:
            self._config['CONNECTION_REQUEST_TIMEOUT'] = int(new_timeout)
        else:
            raise ValueError('new timeout value must be at least 1000 milliseconds')
        
class HttpOptions(Options):
    def __init__(self,
            api_key='CaliperKey',
            host='http://httpbin.org/post',
            connection_timeout=10000,
            so_timeout=10000,
            connection_request_timeout=10000):
        Options.__init__(self)
        self.API_KEY=api_key
        self.HOST=host
        self.CONNECTION_TIMEOUT=connection_timeout
        self.SO_TIMEOUT=so_timeout
        self.CONNECTION_REQUEST_TIMEOUT=connection_request_timeout

### Caliper serializable base class for all caliper objects that need serialization ###
class CaliperSerializable(object):
    def __init__(self):
        self._objects = {}
        self._props = {}

    def _set_object(self,k,v):
        self._objects.update({k:v})

    def _set_prop(self,k,v):
        self._props.update({k:v})

    def _set_float_prop(self,k,v):
        if v == None:
            self._set_prop(k,None)
        else:
            self._set_prop(k, float(v))

    def _set_bool_prop(self,k,v):
        if v == None:
            self._set_prop(k, None)
        else:
            self._set_prop(k, bool(v))

    def _set_id_prop(self,k,v):
        self._set_str_prop(k, getattr(v, 'id', None))
        self._set_object(k,v)
            
    def _set_int_prop(self,k,v):
        if v == None:
            self._set_prop(k,None)
        else:
            self._set_prop(k, int(v))

    def _set_list_prop(self,k,v):
        self._set_prop(k,v or [])

    def _append_list_prop(self,k,v):
        if (not k in self._props) or (self._props[k] is None):
            self._set_list_prop(k,[v])
        elif isinstance(self._props[k], collections.MutableSequence):
            self._props[k].append(v)
        else:
            raise ValueError('attempt to append to a non-list property')

    def _set_obj_prop(self,k,v):
        self._set_prop(k,v)

    def _set_str_prop(self,k,v):
        if v == None:
            self._set_prop(k,None)
        else:
            self._set_prop(k, str(v))

    def _get_object(self,k):
        try:
            return self._objects[k]
        except KeyError:
            return None

    def _get_prop(self,k):
        try:
            return self._props[k]
        except KeyError:
            return None

    def _unpack_list(self,l):
        r = []
        for item in l:
            if isinstance(item, collections.MutableSequence):
                r.append(self._unpack_list(item))
            elif isinstance(item, CaliperSerializable):
                r.append(item.as_dict())
            else:
                r.append(item)
        return r

    def as_dict(self):
        r = {}
        for k,v in self._props.items():

            # handle value based on its type: list, composite, or basic type
            if isinstance(v, collections.MutableSequence):
                value = self._unpack_list(v)
            elif isinstance(v, CaliperSerializable):
                value = v.as_dict()
            else:
                value = v
            r.update({k:value})
            
        return copy.deepcopy(r)

    def as_json(self):
        return json.dumps(self.as_dict(),sort_keys=True)

### Entities ###
class MetaEntity(type):
    @property
    def Types(cls):
        return cls._types

@six.add_metaclass(MetaEntity)
class BaseEntity(CaliperSerializable):
    def __init__(self, **kwargs):
        CaliperSerializable.__init__(self)
    pass

### Events ###
class MetaEvent(type):
    @property
    def Types(cls):
        return cls._types

    @property
    def Contexts(cls):
        return cls._contexts

@six.add_metaclass(MetaEvent)
class BaseEvent(CaliperSerializable):
    def __init__(self, **kwargs):
        CaliperSerializable.__init__(self)

### Profiles ###
class MetaProfile(type):
    @property
    def Actions(cls):
        return cls._actions

@six.add_metaclass(MetaProfile)
class BaseProfile(object):
    pass

### Roles ###
class MetaRole(type):
    @property
    def Roles(cls):
        return cls._roles

@six.add_metaclass(MetaRole)
class BaseRole(object):
    pass

### Statuses ###
class MetaStatus(type):
    @property
    def Statuses(cls):
        return cls._statuses

@six.add_metaclass(MetaStatus)
class BaseStatus(object):
    pass

