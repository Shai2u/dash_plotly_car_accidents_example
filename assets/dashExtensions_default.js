window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, latlng, context) {
            circleOptions = {
                fillOpacity: 0,
                stroke: false,
                radius: 0
            };
            return L.circleMarker(latlng, circleOptions); // render a simple circle marker
        },
        function1: function(feature, latlng, context) {
            const {
                active_col,
                circleOptions,
                color_dict
            } = context.hideout;
            const active_col_val = feature.properties[active_col];
            circleOptions.fillColor = color_dict[active_col][active_col_val];
            return L.circleMarker(latlng, circleOptions); // render a simple circle marker
        },
        function2: function(feature, layer, context) {
            layer.bindTooltip(`${feature.properties.HODESH_TEUNA} (${feature.properties[feature.properties.active_col]})`)
        }
    }
});