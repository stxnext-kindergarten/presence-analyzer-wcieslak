google.load("visualization", "1", {packages:["corechart"], 'language': 'pl'});

(function($) {
    $(document).ready(function() {
        var loading = $('#loading');
        $.getJSON("/api/v1/users", function(result) {
            var dropdown = $("#user_id");
            $.each(result, function(key, value) {
                dropdown.append($("<option />").val(value.id).text(value.name));
            });
            dropdown.show();
            loading.hide();
        });
        $('#user_id').change(function() {
            var selected_user = $("#user_id").val(),
                chart_div = $('#chart_div'),
                avatar_div = $('#avatar'),
                avatar_img = $('#avatar img'),
                no_data_div = $('#no_data');
            if(selected_user) {
                no_data_div.hide();
                loading.show();
                avatar_div.hide();
                chart_div.hide();
                $.getJSON("/api/v1/mean_time_weekday/"+selected_user, function(result) {
                    $.each(result, function(index, value) {
                        value[1] = parseInterval(value[1]);
                    });
                    var data = new google.visualization.DataTable();
                    data.addColumn('string', 'Weekday');
                    data.addColumn('datetime', 'Mean time (h:m:s)');
                    data.addRows(result);
                    var options = {
                        hAxis: {title: 'Weekday'}
                    },
                        formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'});
                    formatter.format(data, 1);
                    $.get("/api/v1/users/"+selected_user, function(data) {
                        avatar_img.attr('src', data.image);
                    });
                    avatar_div.show();
                    chart_div.show();
                    loading.hide();
                    var chart = new google.visualization.ColumnChart(chart_div[0]);
                    chart.draw(data, options);
                }).fail(function() {
                    loading.hide();
                    no_data_div.show();
                });
            }
        });
    });
})(jQuery);
