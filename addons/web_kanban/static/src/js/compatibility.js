dotop.define('web_kanban.compatibility', function (require) {
"use strict";

var kanban_widgets = require('web_kanban.widgets');
var KanbanRecord = require('web_kanban.Record');
var KanbanColumn = require('web_kanban.Column');
var KanbanView = require('web_kanban.KanbanView');

return;
dotop = window.dotop || {};
dotop.web_kanban = dotop.web_kanban || {};
dotop.web_kanban.AbstractField = kanban_widgets.AbstractField;
dotop.web_kanban.KanbanGroup = KanbanColumn;
dotop.web_kanban.KanbanRecord = KanbanRecord;
dotop.web_kanban.KanbanView = KanbanView;

});
