/*!
 * Deluge.Sidebar.js
 *
 * Copyright (c) Damien Churchill 2009-2011 <damoxc@gmail.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, write to:
 *     The Free Software Foundation, Inc.,
 *     51 Franklin Street, Fifth Floor
 *     Boston, MA  02110-1301, USA.
 *
 * In addition, as a special exception, the copyright holders give
 * permission to link the code of portions of this program with the OpenSSL
 * library.
 * You must obey the GNU General Public License in all respects for all of
 * the code used other than OpenSSL. If you modify file(s) with this
 * exception, you may extend this exception to your version of the file(s),
 * but you are not obligated to do so. If you do not wish to do so, delete
 * this exception statement from your version. If you delete this exception
 * statement from all source files in the program, then also delete it here.
 */

// These are just so gen_gettext.py will pick up the strings
// _('State')
// _('Tracker Host')

/**
 * @class Deluge.Sidebar
 * @author Damien Churchill <damoxc@gmail.com>
 * @version 1.3
 */
Ext.define('Deluge.Sidebar', {
    extend: 'Ext.panel.Panel',

    id: 'sidebar',
    region: 'west',
    cls: 'deluge-sidebar',
    title: _('Filters'),
    layout: 'accordion',
    layoutCfg: {
        multi: true,
        collapseFirst: true
    },
    split: true,
    width: 200,
    minSize: 100,
    collapsible: true,
    margins: '5 0 0 5',
    cmargins: '5 0 0 5',

    // private
    panels: {},

    // private
    selected: null,

    // private
    initComponent: function() {
        this.callParent(arguments);
        deluge.events.on("disconnect", this.onDisconnect, this);
    },

    createFilter: function(filter, states) {
        var panel = Ext.create('Deluge.FilterPanel', {
            filter: filter,
            // FIXME an attemp to fix panel.header click
            //~ listeners: {
                //~ click: function() {
                    //~ console.log("SFS")
                    //~ var s = panel.getStore(),
                    //~ sm = panel.getSelectionModel();

                    //~ if (!deluge.config.sidebar_multiple_filters) {
                        //~ deluge.ui.update();
                    //~ };
                    //~ if (!sm.hasSelection() && s.count() > 0) {
                        //~ sm.select([s.first()]);
                    //~ };
            //~ }}
        });
        panel.on('selectionchange', function(view, nodes) {
            deluge.ui.update();
        });

        this.add(panel);

        this.doLayout();
        this.panels[filter] = panel;

        //~ panel.header.on('click', function(header) {
            //~ var s = panel.getStore(),
                //~ sm = panel.getSelectionModel();

            //~ if (!deluge.config.sidebar_multiple_filters) {
                //~ deluge.ui.update();
            //~ }

            //~ if (!sm.hasSelection() && s.count() > 0) {
                //~ sm.select([s.first()]);
            //~ }
        //~ });

        this.fireEvent('filtercreate', this, panel);

        panel.updateStates(states);
        this.fireEvent('afterfiltercreate', this, panel);
    },

    getFilter: function(filter) {
        return this.panels[filter];
    },

    getFilterStates: function() {
        var states = {}

        if (deluge.config.sidebar_multiple_filters) {
            // Grab the filters from each of the filter panels
            this.items.each(function(panel) {
                var state = panel.getState();
                if (state == null) return;
                states[panel.filterType] = state;
            }, this);
        } else {
            var panel = this.getLayout().activeItem;
            if (panel) {
                var state = panel.getState();
                if (!state == null) return;
                states[panel.filterType] = state;
            }
        }

        return states;
    },

    hasFilter: function(filter) {
        return (this.panels[filter]) ? true : false;
    },

    // private
    onDisconnect: function() {
        for (var filter in this.panels) {
            this.remove(this.panels[filter]);
        }
        this.panels = {};
        this.selected = null;
    },

    onFilterSelect: function(selModel, rowIndex, record) {
        deluge.ui.update();
    },

    update: function(filters) {
        for (var filter in filters) {
            var states = filters[filter];
            if (Ext.getKeys(this.panels).indexOf(filter) > -1) {
                this.panels[filter].updateStates(states);
            } else {
                this.createFilter(filter, states);
            }
        }

        // Perform a cleanup of fitlers that are not enabled any more.
        Ext.each(Ext.keys(this.panels), function(filter) {
            if (Ext.keys(filters).indexOf(filter) == -1) {
                // We need to remove the panel
                this.remove(this.panels[filter]);
                this.doLayout();
                delete this.panels[filter];
            }
        }, this);
    }
});
