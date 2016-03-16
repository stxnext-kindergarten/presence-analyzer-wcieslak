google.load("visualization", "1", {packages:["corechart"], 'language': 'en'});

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
                avatar_img = $('#avatar img');
            if(selected_user) {
                loading.show();
                avatar_div.hide();
                chart_div.hide();
                $.getJSON("/api/v1/presence_weekday/"+selected_user, function(result) {
                    var data = google.visualization.arrayToDataTable(result),
                        options = {};
                    $.get("/api/v1/users/"+selected_user, function(data) {
                        avatar_img.attr('src', data.image);
                    });
                    avatar_div.show();
                    chart_div.show();
                    loading.hide();
                    var chart = new google.visualization.PieChart(chart_div[0]);
                    chart.draw(data, options);
                });
            }
        });
    });
})(jQuery);
