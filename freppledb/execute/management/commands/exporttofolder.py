#
# Copyright (C) 2016 by frePPLe bv
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

import os
import errno
import gzip
import logging

from _datetime import datetime
from time import localtime, strftime
from django.conf import settings
from django.db import connections, DEFAULT_DB_ALIAS
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.utils.translation import gettext_lazy as _

from freppledb.common.middleware import _thread_locals
from freppledb.common.models import User
from freppledb.common.report import GridReport
from freppledb import VERSION
from freppledb.execute.models import Task
from freppledb.output.views import resource
from freppledb.output.views import buffer

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = """
    Exports tables from the frePPLe database to CSV files in a folder
    """

    requires_system_checks = False

    # Any sql statements that should be executed before the export
    pre_sql_statements = ()

    # Any SQL statements that should be executed before the export
    post_sql_statements = ()

    statements = [
        {
            "filename": "purchaseorder.csv",
            "folder": "export",
            "sql": """COPY
          (select source, lastmodified, reference, status , reference, quantity,
          to_char(startdate,'YYYY-MM-DD HH24:MI:SS') as "ordering date",
          to_char(enddate,'YYYY-MM-DD HH24:MI:SS') as "receipt date",
          criticality, EXTRACT(EPOCH FROM delay) as delay,
          owner_id, item_id, location_id, supplier_id from operationplan
          where status <> 'confirmed' and type='PO')
          TO STDOUT WITH CSV HEADER""",
        },
        {
            "filename": "distributionorder.csv",
            "folder": "export",
            "sql": """COPY
          (select source, lastmodified, reference, status, reference, quantity,
          to_char(startdate,'YYYY-MM-DD HH24:MI:SS') as "ordering date",
          to_char(enddate,'YYYY-MM-DD HH24:MI:SS') as "receipt date",
          criticality, EXTRACT(EPOCH FROM delay) as delay,
          plan, destination_id, item_id, origin_id from operationplan
          where status <> 'confirmed' and type='DO')
          TO STDOUT WITH CSV HEADER""",
        },
        {
            "filename": "manufacturingorder.csv",
            "folder": "export",
            "sql": """COPY
          (select source, lastmodified, reference, status ,reference ,quantity,
          to_char(startdate,'YYYY-MM-DD HH24:MI:SS') as startdate,
          to_char(enddate,'YYYY-MM-DD HH24:MI:SS') as enddate,
          criticality, EXTRACT(EPOCH FROM delay) as delay,
          operation_id, owner_id, plan, item_id
          from operationplan where status <> 'confirmed' and type='MO')
          TO STDOUT WITH CSV HEADER""",
        },
        {
            "filename": "problems.csv",
            "folder": "export",
            "sql": """COPY (
          select
            entity, owner, name, description, startdate, enddate, weight
          from out_problem
          where name <> 'material excess'
          order by entity, name, startdate
          ) TO STDOUT WITH CSV HEADER""",
        },
        {
            "filename": "operationplanmaterial.csv",
            "folder": "export",
            "sql": """COPY (
          select
            item_id as item, location_id as location, quantity,
            flowdate as date, onhand, operationplan_id as operationplan, status
          from operationplanmaterial
          order by item_id, location_id, flowdate, quantity desc
          ) TO STDOUT WITH CSV HEADER""",
        },
        {
            "filename": "operationplanresource.csv",
            "folder": "export",
            "sql": """COPY (
          select
            resource_id as resource, startdate, enddate, setup,
            operationplan_id as operationplan, status
          from operationplanresource
          order by resource_id, startdate, quantity
          ) TO STDOUT WITH CSV HEADER""",
        },
        {
            "filename": "capacityreport.csv",
            "folder": "export",
            "report": resource.OverviewReport,
            "data": {
                "format": "csvlist",
                "buckets": "week",
                "horizontype": True,
                "horizonunit": "month",
                "horizonlength": 6,
            },
        },
        {
            "filename": "inventoryreport.csv",
            "folder": "export",
            "report": buffer.OverviewReport,
            "data": {
                "format": "csvlist",
                "buckets": "week",
                "horizontype": True,
                "horizonunit": "month",
                "horizonlength": 6,
            },
        },
    ]

    def get_version(self):
        return VERSION

    def add_arguments(self, parser):
        parser.add_argument("--user", help="User running the command")
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help="Nominates a specific database to load the data into",
        )
        parser.add_argument(
            "--task",
            type=int,
            help="Task identifier (generated automatically if not provided)",
        )

    def handle(self, *args, **options):
        # Pick up the options
        now = datetime.now()
        self.database = options["database"]
        if self.database not in settings.DATABASES:
            raise CommandError("No database settings known for '%s'" % self.database)

        if options["user"]:
            try:
                self.user = (
                    User.objects.all()
                    .using(self.database)
                    .get(username=options["user"])
                )
            except Exception:
                raise CommandError("User '%s' not found" % options["user"])
        else:
            self.user = None

        timestamp = now.strftime("%Y%m%d%H%M%S")
        if self.database == DEFAULT_DB_ALIAS:
            logfile = "exporttofolder-%s.log" % timestamp
        else:
            logfile = "exporttofolder_%s-%s.log" % (self.database, timestamp)

        try:
            handler = logging.FileHandler(
                os.path.join(settings.FREPPLE_LOGDIR, logfile), encoding="utf-8"
            )
            # handler.setFormatter(logging.Formatter(settings.LOGGING['formatters']['simple']['format']))
            logger.addHandler(handler)
            logger.propagate = False
        except Exception as e:
            print(
                "%s Failed to open logfile %s: %s"
                % (datetime.now().replace(microsecond=0), logfile, e)
            )

        task = None
        errors = 0
        try:
            # Initialize the task
            setattr(_thread_locals, "database", self.database)
            if options["task"]:
                try:
                    task = (
                        Task.objects.all().using(self.database).get(pk=options["task"])
                    )
                except Exception:
                    raise CommandError("Task identifier not found")
                if (
                    task.started
                    or task.finished
                    or task.status != "Waiting"
                    or task.name not in ("frepple_exporttofolder", "exporttofolder")
                ):
                    raise CommandError("Invalid task identifier")
                task.status = "0%"
                task.started = now
                task.logfile = logfile
            else:
                task = Task(
                    name="exporttofolder",
                    submitted=now,
                    started=now,
                    status="0%",
                    user=self.user,
                    logfile=logfile,
                )
            task.arguments = " ".join(['"%s"' % i for i in args])
            task.processid = os.getpid()
            task.save(using=self.database)

            # Execute
            if os.path.isdir(settings.DATABASES[self.database]["FILEUPLOADFOLDER"]):
                if not os.path.isdir(
                    os.path.join(
                        settings.DATABASES[self.database]["FILEUPLOADFOLDER"], "export"
                    )
                ):
                    try:
                        os.makedirs(
                            os.path.join(
                                settings.DATABASES[self.database]["FILEUPLOADFOLDER"],
                                "export",
                            )
                        )
                    except OSError as exception:
                        if exception.errno != errno.EEXIST:
                            raise

                logger.info(
                    "%s Started export to folder\n"
                    % datetime.now().replace(microsecond=0)
                )

                cursor = connections[self.database].cursor()

                task.status = "0%"
                task.save(using=self.database)

                i = 0
                cnt = len(self.statements)

                # Calling all the pre-sql statements
                for stmt in self.pre_sql_statements:
                    try:
                        logger.info("Executing pre-statement '%s'" % stmt)
                        cursor.execute(stmt)
                        logger.info("%s record(s) modified" % cursor.rowcount)
                    except Exception:
                        errors += 1
                        logger.error(
                            "An error occurred when executing statement '%s'" % stmt
                        )

                for cfg in self.statements:
                    # Validate filename
                    filename = cfg.get("filename", None)
                    if not filename:
                        raise Exception("Missing filename in export configuration")
                    folder = cfg.get("folder", None)
                    if not folder:
                        raise Exception(
                            "Missing folder in export configuration for %s" % filename
                        )

                    # Report progress
                    logger.info(
                        "%s Started export of %s"
                        % (datetime.now().replace(microsecond=0), filename)
                    )
                    if task:
                        task.message = "Exporting %s" % filename
                        task.save(using=self.database)

                    # Make sure export folder exists
                    exportFolder = os.path.join(
                        settings.DATABASES[self.database]["FILEUPLOADFOLDER"], folder
                    )
                    if not os.path.isdir(exportFolder):
                        os.makedirs(exportFolder)

                    try:
                        reportclass = cfg.get("report", None)
                        sql = cfg.get("sql", None)
                        if reportclass:
                            # Export from report class

                            # Create a dummy request
                            factory = RequestFactory()
                            request = factory.get("/dummy/", cfg.get("data", {}))
                            if self.user:
                                request.user = self.user
                            else:
                                request.user = User.objects.all().get(username="admin")
                            request.database = self.database
                            request.LANGUAGE_CODE = settings.LANGUAGE_CODE
                            request.prefs = cfg.get("prefs", None)

                            # Initialize the report
                            if hasattr(reportclass, "initialize"):
                                reportclass.initialize(request)
                            if hasattr(reportclass, "rows"):
                                if callable(reportclass.rows):
                                    request.rows = reportclass.rows(request)
                                else:
                                    request.rows = reportclass.rows
                            if hasattr(reportclass, "crosses"):
                                if callable(reportclass.crosses):
                                    request.crosses = reportclass.crosses(request)
                                else:
                                    request.crosses = reportclass.crosses
                            if reportclass.hasTimeBuckets:
                                reportclass.getBuckets(request)

                            # Write the report file
                            datafile = open(os.path.join(exportFolder, filename), "wb")
                            if filename.endswith(".xlsx"):
                                reportclass._generate_spreadsheet_data(
                                    request,
                                    [request.database],
                                    datafile,
                                    **cfg.get("data", {})
                                )
                            elif filename.endswith(".csv"):
                                for r in reportclass._generate_csv_data(
                                    request, [request.database], **cfg.get("data", {})
                                ):
                                    datafile.write(
                                        r.encode(settings.CSV_CHARSET)
                                        if isinstance(r, str)
                                        else r
                                    )
                            else:
                                raise Exception(
                                    "Unknown output format for %s" % filename
                                )
                        elif sql:
                            # Exporting using SQL
                            if filename.lower().endswith(".gz"):
                                datafile = gzip.open(
                                    os.path.join(exportFolder, filename), "w"
                                )
                            else:
                                datafile = open(
                                    os.path.join(exportFolder, filename), "w"
                                )
                            cursor.copy_expert(sql, datafile)
                        else:
                            raise Exception("Unknown export type for %s" % filename)
                        datafile.close()
                        i += 1

                    except Exception as e:
                        errors += 1
                        logger.error(
                            "%s Failed to export to %s: %s"
                            % (datetime.now().replace(microsecond=0), filename, e)
                        )
                        if task:
                            task.message = "Failed to export %s" % filename

                    task.status = str(int(i / cnt * 100)) + "%"
                    task.save(using=self.database)

                logger.info(
                    "%s Exported %s file(s)\n"
                    % (datetime.now().replace(microsecond=0), cnt - errors)
                )

                for stmt in self.post_sql_statements:
                    try:
                        logger.info("Executing post-statement '%s'" % stmt)
                        cursor.execute(stmt)
                        logger.info("%s record(s) modified" % cursor.rowcount)
                    except Exception:
                        errors += 1
                        logger.error(
                            "An error occured when executing statement '%s'" % stmt
                        )

            else:
                errors += 1
                logger.error(
                    "%s Failed, folder does not exist"
                    % datetime.now().replace(microsecond=0)
                )
                task.message = "Destination folder does not exist"
                task.save(using=self.database)

        except Exception as e:
            logger.error(
                "%s Failed to export: %s" % (datetime.now().replace(microsecond=0), e)
            )
            errors += 1
            if task:
                task.message = "Failed to export"

        finally:
            logger.info(
                "%s End of export to folder\n" % datetime.now().replace(microsecond=0)
            )
            if task:
                if not errors:
                    task.status = "100%"
                    task.message = "Exported %s data files" % (cnt)
                else:
                    task.status = "Failed"
                    #  task.message = "Exported %s data files, %s failed" % (cnt-errors, errors)
                task.finished = datetime.now()
                task.processid = None
                task.save(using=self.database)
            setattr(_thread_locals, "database", None)

    # accordion template
    title = _("Export plan result to folder")
    index = 1200
    help_url = "user-guide/command-reference.html#exporttofolder"

    @staticmethod
    def getHTML(request):

        if (
            "FILEUPLOADFOLDER" not in settings.DATABASES[request.database]
            or not request.user.is_superuser
        ):
            return None

        # Function to convert from bytes to human readabl format
        def sizeof_fmt(num):
            for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
                if abs(num) < 1024.0:
                    return "%3.1f%sB" % (num, unit)
                num /= 1024.0
            return "%.1f%sB" % (num, "Yi")

        # List available data files
        filesexported = []
        if "FILEUPLOADFOLDER" in settings.DATABASES[request.database]:
            exportfolder = os.path.join(
                settings.DATABASES[request.database]["FILEUPLOADFOLDER"], "export"
            )
            if os.path.isdir(exportfolder):
                tzoffset = GridReport.getTimezoneOffset(request)
                for file in os.listdir(exportfolder):
                    if file.endswith((".xlsx", ".xlsx.gz", ".csv", ".csv.gz", ".log")):
                        filesexported.append(
                            [
                                file,
                                strftime(
                                    "%Y-%m-%d %H:%M:%S",
                                    localtime(
                                        os.stat(
                                            os.path.join(exportfolder, file)
                                        ).st_mtime
                                        + tzoffset.total_seconds()
                                    ),
                                ),
                                sizeof_fmt(
                                    os.stat(os.path.join(exportfolder, file)).st_size
                                ),
                            ]
                        )

        return render_to_string(
            "commands/exporttofolder.html",
            {"filesexported": filesexported},
            request=request,
        )
