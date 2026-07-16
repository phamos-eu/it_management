// Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
// For license information, please see license.txt

// Wait for DOM to be ready and GoJS to load
document.addEventListener('DOMContentLoaded', function() {
    // Check if GoJS is loaded
    if (typeof go !== 'object') {
        console.error('GoJS not loaded. Check CDN URL in HTML.');
        return;
    }

    // Initialize the app
    ITLandscapeGraph.init();
});

// Main application namespace
var ITLandscapeGraph = (function() {
    'use strict';

    // Diagram reference
    var diagram = null;
    
    // Current filters
    var currentLandscape = null;
    var currentSolutions = [];
    
    // Node data cache
    var allNodeData = [];
    var allGroupData = [];

    // Initialize the graph
    function init() {
        // Initialize GoJS diagram
        initDiagram();
        
        // Load filter options
        loadLandscapeOptions();
        loadSolutionOptions();
        
        // Set up event listeners
        setupEventListeners();
        
        // Load initial data
        loadGraphData();
    }

    // Initialize the GoJS diagram
    function initDiagram() {
        // Create the diagram
        var $ = go.GraphObject.make;
        diagram = $(go.Diagram, 'graph-container', {
            'undoManager.isEnabled': true,
            'layout': $(go.ForceDirectedLayout, {
                // Use a force-directed layout for natural clustering
                'maxIterations': 200,
                'defaultSpringLength': 30,
                'defaultElectricalCharge': 100,
                'randomNumberGenerator': null  // for deterministic layouts
            }),
            // Enable dragging and zooming
            'allowDrag': true,
            'allowZoom': true,
            'allowHorizontalScroll': true,
            'allowVerticalScroll': true,
            // Styling
            'backgroundColor': '#ffffff',
            'grid.visible': false
        });

        // Define node template (simple circle for MVP)
        diagram.nodeTemplate = $(
            go.Node,
            'Auto',
            $(
                go.Shape,
                'Circle',
                {
                    'fill': '#4CAF50',  // Default green (will be updated based on status later)
                    'stroke': '#388E3C',
                    'strokeWidth': 2,
                    'width': 40,
                    'height': 40
                }
            ),
            $(
                go.TextBlock,
                {
                    'text': '',
                    'margin': 5,
                    'font': '12px Segoe UI, sans-serif',
                    'stroke': '#ffffff',
                    'textAlign': 'center',
                    'maxSize': new go.Size(120, NaN),
                    'wrap': go.TextBlock.WrapDesired
                },
                new go.Binding('text', 'text')
            ),
            {
                // Node click: open the Host Item in a new tab
                'click': function(e, node) {
                    if (node && node.data && node.data.key) {
                        window.open('/app/itm-host-item/' + node.data.key, '_blank');
                    }
                },
                // Node hover: show tooltip
                'mouseEnter': function(e, node) {
                    showTooltip(node);
                },
                'mouseLeave': function(e, node) {
                    hideTooltip();
                }
            }
        );

        // Define group template (for Solutions)
        diagram.groupTemplate = $(
            go.Group,
            'Auto',
            $(
                go.Shape,
                'Rectangle',
                {
                    'fill': 'rgba(200, 200, 255, 0.3)',
                    'stroke': '#4285F4',
                    'strokeWidth': 2
                }
            ),
            $(
                go.TextBlock,
                {
                    'text': '',
                    'margin': 10,
                    'font': 'bold 14px Segoe UI, sans-serif',
                    'stroke': '#1976D2',
                    'textAlign': 'center'
                },
                new go.Binding('text', 'text')
            ),
            {
                // Group click: expand/collapse
                'click': function(e, group) {
                    if (group.isExpanded) {
                        group.collapseGroup();
                    } else {
                        group.expandGroup();
                    }
                },
                // Allow dragging groups
                'allowDrag': true
            }
        );

        // Diagram events
        diagram.addDiagramListener('InitialLayoutCompleted', function() {
            // Fit the diagram to the viewport after initial load
            diagram.scale = 1.0;
            diagram.position = new go.Point(0, 0);
        });
    }

    // Load landscape filter options
    function loadLandscapeOptions() {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'ITM Landscape',
                fields: ['name', 'title'],
                order_by: 'title'
            },
            callback: function(r) {
                if (r.message) {
                    var landscapeSelect = document.getElementById('landscape-filter');
                    var allOption = document.createElement('option');
                    allOption.value = '';
                    allOption.textContent = 'All Landscapes';
                    landscapeSelect.appendChild(allOption);
                    
                    r.message.forEach(function(landscape) {
                        var option = document.createElement('option');
                        option.value = landscape.name;
                        option.textContent = landscape.title || landscape.name;
                        landscapeSelect.appendChild(option);
                    });
                }
            }
        });
    }

    // Load solution filter options
    function loadSolutionOptions() {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'ITM Solution',
                fields: ['name', 'name1'],
                order_by: 'name1'
            },
            callback: function(r) {
                if (r.message) {
                    var solutionSelect = document.getElementById('solution-filter');
                    
                    r.message.forEach(function(solution) {
                        var option = document.createElement('option');
                        option.value = solution.name;
                        option.textContent = solution.name1 || solution.name;
                        solutionSelect.appendChild(option);
                    });
                }
            }
        });
    }

    // Load graph data from API
    function loadGraphData() {
        showLoading();
        
        frappe.call({
            method: 'it_management.api.get_landscape_graph_data',
            args: {
                landscape: currentLandscape,
                solutions: JSON.stringify(currentSolutions)
            },
            callback: function(r) {
                hideLoading();
                if (r.message) {
                    allNodeData = r.message.nodes || [];
                    allGroupData = r.message.groups || [];
                    
                    // Build the diagram model
                    var model = new go.GraphLinksModel();
                    
                    // Add groups first
                    allGroupData.forEach(function(group) {
                        model.addNodeData({
                            key: group.key,
                            text: group.text,
                            isGroup: true,
                            category: 'group'
                        });
                    });
                    
                    // Add nodes
                    allNodeData.forEach(function(node) {
                        // Determine group key (solution)
                        var groupKey = null;
                        if (node.solution) {
                            var solutionGroup = allGroupData.find(function(g) {
                                return g.members && g.members.includes(node.key);
                            });
                            if (solutionGroup) {
                                groupKey = solutionGroup.key;
                            }
                        }
                        
                        model.addNodeData({
                            key: node.key,
                            text: node.text,
                            status: node.status,
                            solution: node.solution,
                            landscape: node.landscape,
                            group: groupKey
                        });
                    });
                    
                    // Add nodes to their groups
                    allGroupData.forEach(function(group) {
                        if (group.members && group.members.length > 0) {
                            group.members.forEach(function(memberKey) {
                                var nodeData = model.findNodeDataByKey(memberKey);
                                if (nodeData) {
                                    model.setGroupKeyForNodeData(nodeData, group.key);
                                }
                            });
                        }
                    });
                    
                    // Set the model
                    diagram.model = model;
                    
                    // Fit the diagram to the viewport
                    diagram.delayUpdate();
                    setTimeout(function() {
                        diagram.fitView();
                    }, 100);
                }
            },
            error: function(r) {
                hideLoading();
                console.error('Error loading graph data:', r);
                frappe.show_alert({message: 'Error loading graph data. See console for details.', indicator: 'red'});
            }
        });
    }

    // Set up event listeners for controls
    function setupEventListeners() {
        // Landscape filter change
        document.getElementById('landscape-filter').addEventListener('change', function(e) {
            currentLandscape = e.target.value || null;
            loadGraphData();
        });
        
        // Solution filter change (multi-select)
        document.getElementById('solution-filter').addEventListener('change', function(e) {
            var selected = [];
            var options = e.target.selectedOptions;
            for (var i = 0; i < options.length; i++) {
                if (options[i].value) {
                    selected.push(options[i].value);
                }
            }
            currentSolutions = selected.length > 0 ? selected : null;
            loadGraphData();
        });
        
        // Search box
        document.getElementById('search-box').addEventListener('input', function(e) {
            var searchTerm = e.target.value.toLowerCase();
            if (!searchTerm) {
                // If search is empty, show all nodes
                diagram.model.nodeDataArray.forEach(function(nodeData) {
                    diagram.model.setVisible(nodeData, true);
                });
                return;
            }
            
            // Filter nodes based on search term
            diagram.model.nodeDataArray.forEach(function(nodeData) {
                var text = (nodeData.text || '').toLowerCase();
                var isVisible = text.includes(searchTerm);
                diagram.model.setVisible(nodeData, isVisible);
            });
        });
        
        // Export as PNG
        document.getElementById('export-png').addEventListener('click', function() {
            var imgData = diagram.makeImageData({
                scale: 1.0,
                background: '#ffffff'
            });
            
            var img = new Image();
            img.onload = function() {
                var canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                var ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                
                var link = document.createElement('a');
                link.download = 'it-landscape-graph.png';
                link.href = canvas.toDataURL('image/png');
                link.click();
            };
            img.src = imgData;
        });
        
        // Reset view
        document.getElementById('reset-view').addEventListener('click', function() {
            diagram.scale = 1.0;
            diagram.position = new go.Point(0, 0);
            diagram.fitView();
        });
    }

    // Show tooltip for a node
    function showTooltip(node) {
        if (!node || !node.data) return;
        
        var tooltip = document.getElementById('node-tooltip');
        var data = node.data;
        
        var content = '<div><strong>' + (data.text || data.key) + '</strong></div>';
        if (data.status) {
            content += '<div>Status: ' + data.status + '</div>';
        }
        if (data.solution) {
            content += '<div>Solution: ' + data.solution + '</div>';
        }
        if (data.landscape) {
            content += '<div>Landscape: ' + data.landscape + '</div>';
        }
        
        tooltip.innerHTML = content;
        tooltip.style.display = 'block';
        
        // Position tooltip near the node
        var nodeBounds = node.actualBounds;
        var diagramPos = diagram.lastInput.viewPoint;
        tooltip.style.left = (diagramPos.x + 20) + 'px';
        tooltip.style.top = (diagramPos.y + 20) + 'px';
    }

    // Hide tooltip
    function hideTooltip() {
        var tooltip = document.getElementById('node-tooltip');
        tooltip.style.display = 'none';
    }

    // Show loading indicator
    function showLoading() {
        diagram.div.style.opacity = '0.5';
    }

    // Hide loading indicator
    function hideLoading() {
        diagram.div.style.opacity = '1';
    }

    // Public API
    return {
        init: init,
        loadGraphData: loadGraphData
    };
})();
