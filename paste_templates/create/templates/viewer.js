<%inherit file="viewer_base.js"/>

<%block name="init_project">\
    OpenLayers.ImgPath = "$${request.static_url('${package}:static/lib/cgxp/core/src/theme/img/ol/')}";
    Ext.BLANK_IMAGE_URL = "$${request.static_url('${package}:static/lib/cgxp/ext/Ext/resources/images/default/s.gif')}";
</%block>\
<%block name="wmts_options_settings">\
    style: 'default',
    dimensions: ['TIME'],
    params: {
        'time': '2011'
    },
    matrixSet: 'swissgrild',
    maxExtent: new OpenLayers.Bounds(420000, 30000, 900000, 350000),
    projection: new OpenLayers.Projection("EPSG:21781"),
    units: "m",
    formatSuffix: 'png',
    serverResolutions: [4000,3750,3500,3250,3000,2750,2500,2250,2000,1750,1500,1250,1000,750,650,500,250,100,50,20,10,5,2.5,2,1.5,1,0.5,0.25,0.1,0.05],
</%block>\
<%block name="default_initial_extent">\
    var INITIAL_EXTENT = [420000, 30000, 900000, 350000];
</%block>\
<%block name="restricted_extent">\
    var RESTRICTED_EXTENT = [420000, 30000, 900000, 350000];
</%block>\
<%block name="viewer_map_options">\
    projection: new OpenLayers.Projection("EPSG:21781"),
    units: "m",
    resolutions: [4000,2000,1000,500,250,100,50,20,10,5,2.5,1,0.5,0.25,0.1,0.05],
</%block>\
<%block name="viewer_tools_layertree_options">\
    defaultThemes: ["Default"],
</%block>\
<%block name="viewer_tools_querier_options">\
    srsName: 'EPSG:21781',
    featureType: "Layer_Query",
</%block>\
<%block name="viewer_tools_toolbar_help_options">\
    url: "$${request.static_url('${package}:static/app/pdf/help.pdf')}",
</%block>\
<%block name="viewer_add_controls">\
    // Static image version
    /*
    return new OpenLayers.Control.OverviewMap({
        size: new OpenLayers.Size(200, 100),
        layers: [new OpenLayers.Layer.Image(
            "Overview Map",
            "$${request.static_url('${package}:static/images/overviewmap.png')}",
            OpenLayers.Bounds.fromArray([420000, 30000, 900000, 350000]),
            new OpenLayers.Size([200, 100]),
            {isBaseLayer: true}
        )],
        mapOptions: {
            numZoomLevels: 1
        }
    })*/
    // OSM version
    new OpenLayers.Control.OverviewMap({
        size: new OpenLayers.Size(200, 100),
        minRatio: 64, 
        maxRatio: 64, 
        layers: [new OpenLayers.Layer.OSM("OSM", [
                'http://a.tile.openstreetmap.org/$${"$${z}"}/$${"$${x}"}/$${"$${y}"}.png',
                'http://b.tile.openstreetmap.org/$${"$${z}"}/$${"$${x}"}/$${"$${y}"}.png',
                'http://c.tile.openstreetmap.org/$${"$${z}"}/$${"$${x}"}/$${"$${y}"}.png'
            ], {
                transitionEffect: 'resize',
                attribution: [
                    "(c) <a href='http://openstreetmap.org/'>OSM</a>",
                    "<a href='http://creativecommons.org/licenses/by-sa/2.0/'>by-sa</a>"
                ].join(' ')
            }
        )]
    })
</%block>\
<%block name="viewer_layers">\
    {
        source: "olsource",
        type: "OpenLayers.Layer.WMTS",
        args: [Ext.applyIf({
            name: OpenLayers.i18n('ortho'),
            mapserverLayers: 'ortho',
            ref: 'ortho',
            layer: 'ortho',
            formatSuffix: 'jpeg',
            opacity: 0
        }, WMTS_OPTIONS)]
    }, {
        source: "olsource",
        type: "OpenLayers.Layer.WMTS",
        group: 'background',
        args: [Ext.applyIf({
            name: OpenLayers.i18n('plan'),
            mapserverLayers: 'plan',
            ref: 'plan',
            layer: 'plan',
            group: 'background'
        }, WMTS_OPTIONS)]
    }, 
</%block>\
