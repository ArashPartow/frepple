# Copyright (C) 2013 by frePPLe bv
#
# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from django.conf import settings
from django.utils.translation import gettext_lazy as _

import freppledb.common.views
from freppledb.common.models import User, Bucket, BucketDetail, Parameter, Comment
from freppledb.menu import menu
from freppledb import __version__


# Settings menu
menu.addItem(
    "admin",
    "parameter admin",
    url="/data/common/parameter/",
    report=freppledb.common.views.ParameterList,
    index=1100,
    model=Parameter,
    admin=True,
)
menu.addItem(
    "admin",
    "bucket admin",
    url="/data/common/bucket/",
    report=freppledb.common.views.BucketList,
    index=1200,
    model=Bucket,
    admin=True,
)
menu.addItem(
    "admin",
    "bucketdetail admin",
    url="/data/common/bucketdetail/",
    report=freppledb.common.views.BucketDetailList,
    index=1300,
    model=BucketDetail,
    admin=True,
)
menu.addItem(
    "admin",
    "comment admin",
    url="/data/common/comment/",
    report=freppledb.common.views.CommentList,
    index=1400,
    model=Comment,
    admin=True,
)

# User maintenance
menu.addItem("admin", "users", separator=True, index=2000)
menu.addItem(
    "admin",
    "user admin",
    url="/data/common/user/",
    report=freppledb.common.views.UserList,
    index=2100,
    model=User,
    admin=True,
)
menu.addItem(
    "admin",
    "group admin",
    url="/data/auth/group/",
    report=freppledb.common.views.GroupList,
    index=2200,
    permission="auth.change_group",
    admin=True,
)

# Help menu
try:
    versionnumber = __version__.split(".", 2)
    docurl = "%s/docs/%s.%s/index.html" % (
        settings.DOCUMENTATION_URL,
        versionnumber[0],
        versionnumber[1],
    )
except Exception:
    docurl = "%s/docs/current/index.html" % (settings.DOCUMENTATION_URL,)
menu.addItem(
    "help",
    "documentation",
    url=docurl,
    label=_("Documentation"),
    window=True,
    prefix=False,
    index=300,
)
menu.addItem(
    "help",
    "API",
    url="/api/",
    label=_("REST API help"),
    window=True,
    prefix=True,
    index=400,
)
menu.addItem(
    "help",
    "website",
    url="https://frepple.com",
    window=True,
    label=_("frePPLe website"),
    prefix=False,
    index=500,
)
menu.addItem(
    "help", "about", javascript="about_show()", label=_("About frePPLe"), index=600
)
