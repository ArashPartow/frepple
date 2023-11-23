/*
 * Copyright (C) 2023 by frePPLe bv
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files (the
 * "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 * LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 * WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
 */

angular.module('operationplandetailapp').directive('showGanttDrv', showGanttDrv);

showKanbanDrv.$inject = ['$window', 'gettextCatalog', 'OperationPlan', 'PreferenceSvc'];

function showGanttDrv($window, gettextCatalog, OperationPlan, PreferenceSvc) {
  'use strict';

  var directive = {
    restrict: 'EA',
    scope: {
      ganttoperationplans: '=',
      editable: '='
    },
    templateUrl: '/static/operationplandetail/gantt.html',
    link: linkfunc
  };
  return directive;

  function linkfunc($scope, $elem, attrs) {
    $scope.rowheight = 25;
    $scope.curselected = null;
    $scope.colstyle = 'col-md-1';
    $scope.type = 'PO';
    $scope.admin_escape = admin_escape;
    $scope.url_prefix = url_prefix;
    $scope.mode = mode;

    $scope.$watch('ganttoperationplans', function () {
      $scope.drawGantt();
    });

    function getHeight(gutter) {
      if (preferences && preferences['height'])
        return preferences['height'] - (gutter || 25);
      else
        return 220;
    }
    $scope.getHeight = getHeight;

    function getDirtyCards() {
      console.log("getting changes");
      return 111;
    }
    $scope.getDirtyCards = getDirtyCards;

    function findOperationPlan(ref) {
      return $scope.ganttoperationplans.rows ?
        $scope.ganttoperationplans.rows.find(e => { return e.operationplan__reference == ref; }) :
        null;
    }
    $scope.findOperationPlan = findOperationPlan;

    function buildtooltip() {
      var opplan = $scope.findOperationPlan($(this).attr("data-reference"));
      var extra = '';
      var thedelay = Math.round(opplan.operationplan__delay / 8640) / 10;
      if (thedelay < 0.1)
        thedelay = "" + (-thedelay) + " " + gettext("days early");
      else if (thedelay > 0.1)
        thedelay = "" + thedelay + " " + gettext("days late");
      else
        thedelay = gettext("on time");
      if (opplan.operationplan__operation__description)
        extra += gettext('description') + ": " + opplan.operationplan__operation__description + '<br>';
      if (opplan.operationplan__batch)
        extra += gettext('batch') + ": " + opplan.operationplan__batch + '<br>';
      if (opplan.operationplan__type === 'MO') {
        return gettext('manufacturing order') + '<br>' +
          opplan.operationplan__operation__name + '<br>' +
          gettext('reference') + ": " + opplan.operationplan__reference + '<br>' +
          extra +
          gettext('start') + ": " + moment(opplan.operationplan__startdate).format(datetimeformat) + '<br>' +
          gettext('end') + ": " + moment(opplan.operationplan__enddate).format(datetimeformat) + '<br>' +
          gettext('quantity') + ": " + grid.formatNumber(opplan.operationplan__quantity) + "<br>" +
          gettext('criticality') + ": " + opplan.operationplan__criticality + "<br>" +
          gettext('delay') + ": " + thedelay + "<br>" +
          gettext('status') + ": " + gettext(opplan.operationplan__status) + "<br>";
      }
      else if ($(this).attr("data-type") === 'PO') {
        return gettext('purchase order') + '<br>' +
          opplan.operationplan__item__name + ' @ ' + opplan.operationplan__location__name + '<br>' +
          gettext('reference') + ": " + opplan.operationplan__reference + '<br>' +
          extra +
          gettext('start') + ": " + moment(opplan.operationplan__startdate).format(datetimeformat) + '<br>' +
          gettext('end') + ": " + moment(opplan.operationplan__enddate).format(datetimeformat) + '<br>' +
          gettext('quantity') + ": " + grid.formatNumber(opplan.operationplan__quantity) + "<br>" +
          gettext('criticality') + ": " + opplan.operationplan__criticality + "<br>" +
          gettext('delay') + ": " + thedelay + "<br>" +
          gettext('status') + ": " + gettext(opplan.operationplan__status) + "<br>";
      }
      else if ($(this).attr("data-type") === 'DO') {
        return gettext('distribution order') + '<br>' +
          opplan.operationplan__item__name + ' @ ' + opplan.operationplan__location__name + '<br>' +
          gettext('origin') + ": " + opplan.operationplan__origin__name + '<br>' +
          gettext('reference') + ": " + opplan.operationplan__reference + '<br>' +
          extra +
          gettext('start') + ": " + moment(opplan.operationplan__startdate).format(datetimeformat) + '<br>' +
          gettext('end') + ": " + moment(opplan.operationplan__enddate).format(datetimeformat) + '<br>' +
          gettext('quantity') + ": " + grid.formatNumber(opplan.operationplan__quantity) + "<br>" +
          gettext('criticality') + ": " + opplan.operationplan__criticality + "<br>" +
          gettext('delay') + ": " + thedelay + "<br>" +
          gettext('status') + ": " + gettext(opplan.operationplan__status) + "<br>";
      }
      else if ($(this).attr("data-type") === 'STCK') {
        return gettext('inventory') + '<br>' +
          opplan.operationplan__item__name + ' @ ' + opplan.operationplan__location__name + '<br>' +
          gettext('quantity') + ": " + grid.formatNumber(opplan.operationplan__quantity) + "<br>";
      }
      else if ($(this).attr("data-type") === 'DLVR') {
        return gettext('customer delivery') + '<br>' +
          extra +
          opplan.operationplan__item__name + ' @ ' + opplan.operationplan__location__name + '<br>' +
          gettext('demand') + ": " + opplan.operationplan__demand__name + '<br>' +
          gettext('start') + ": " + moment(opplan.operationplan__startdate).format(datetimeformat) + '<br>' +
          gettext('end') + ": " + moment(opplan.operationplan__enddate).format(datetimeformat) + '<br>' +
          gettext('quantity') + ": " + grid.formatNumber(opplan.operationplan__quantity) + "<br>" +
          gettext('criticality') + ": " + opplan.operationplan__criticality + "<br>" +
          gettext('delay') + ": " + thedelay + "<br>" +
          gettext('status') + ": " + gettext(opplan.operationplan__status) + "<br>";
      }
    }
    $scope.buildtooltip = buildtooltip;

    function buildcolor(opplan) {
      return "red";
    }
    $scope.buildcolor = buildcolor;

    function time2scale(d) {
      return Math.round((d - horizonstart) / (horizonend - horizonstart) * 1000);
    }
    $scope.time2scale = time2scale;

    function duration2scale(d) {
      return Math.round(d / (horizonend - horizonstart) * 1000);
    }
    $scope.duration2scale = duration2scale;

    function drawGantt() {
      if (!$scope.ganttoperationplans.rows) return;
      var data = '<table class="table"><tr><th>resource</th><th id="ganttheader"></th></tr>';
      var curresource;
      var first = true;
      var layer = [];
      var svgdata = "";
      for (var opplan of $scope.ganttoperationplans.rows) {
        if (opplan.resource != curresource) {
          curresource = opplan.resource;
          if (!first) {
            data += '<svg viewbox="0 0 1000 '
              + (layer.length * $scope.rowheight) + '" width="100%" height="'
              + (layer.length * $scope.rowheight) + 'px">' +
              + '<g class="ganttrow" transform="scale(' + 1 + ',1) translate(0,' + ((layer.length - 1) * $scope.rowheight + 3) + ')" title="' + layer.length + '">'
              + svgdata + "</g></svg></td></tr>";
          }
          first = false;
          data += "<tr><td>" + opplan.resource + '</td><td>';
          layer = [];
          svgdata = "";
        }

        var row = 0;
        for (; row < layer.length; ++row) {
          if (new Date(opplan["startdate"]) >= layer[row] && (opplan["enddate"] != opplan["startdate"])) {
            layer[row] = new Date(opplan["enddate"]);
            break;
          }
        };
        if (row >= layer.length) layer.push(new Date(opplan["enddate"]));

        svgdata += '<rect class="opplan" x="' + time2scale(new Date(opplan.startdate))
          + '" y="' + (-row * $scope.rowheight)
          + '" fill="' + buildcolor(opplan)
          + '" width="' + duration2scale(opplan.enddate - opplan.startdate)
          + '" height="' + ($scope.rowheight - 3)
          + '" data-reference="' + encodeURI(opplan.operationplan__reference) + '"';
        if (opplan["status"] == "proposed")
          svgdata += ' fill-opacity="0.5"/>';
        else
          svgdata += '/>';
      }
      if (!first)
        data += '<svg viewbox="0 0 1000 '
          + (layer.length * $scope.rowheight) + '" width="100%" height="'
          + (layer.length * $scope.rowheight) + 'px">'
          + '<g class="ganttrow" transform="scale(' + 1 + ',1) translate(0,' + ((layer.length - 1) * $scope.rowheight + 3) + ')" title="' + layer.length + '">'
          + svgdata + "</g></svg></td></tr>";
      data += "</table>";
      angular.element(document).find('#ganttgraph').empty().append(data);
      gantt.header("#ganttheader");

      $('svg rect').on("click", function (d) {
        var opplan = $scope.findOperationPlan($(d.target).attr("data-reference"));
        $scope.$parent.displayInfo(opplan);
      }).
        each(function () {
          bootstrap.Tooltip.getOrCreateInstance($(this)[0], {
            title: $scope.buildtooltip,
            animation: false,
            html: true,
            container: 'body',
            template: `
         <div class="tooltip opacity-100" role="tooltip">
           <div class="tooltip-arrow"></div>
           <div class="tooltip-inner bg-white text-start text-body fs-6 p-3"></div>
         </div>`
          });
        });
    }
    $scope.drawGantt = drawGantt;
  }
}