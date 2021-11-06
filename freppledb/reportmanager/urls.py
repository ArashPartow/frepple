#
# Copyright (C) 2019 by frePPLe bv
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

from django.urls import re_path

from .views import ReportManager, ReportList, getSchema

# Automatically add these URLs when the application is installed
autodiscover = True

urlpatterns = [
    re_path(r"^reportmanager/schema/$", getSchema, name="reportmanager_schema"),
    re_path(r"^reportmanager/(.+)/$", ReportManager.as_view(), name="reportmanager_id"),
    re_path(r"^reportmanager/$", ReportManager.as_view()),
    re_path(r"^data/reportmanager/sqlreport/add/$", ReportManager.as_view()),
    re_path(r"^data/reportmanager/sqlreport/$", ReportList.as_view()),
]
