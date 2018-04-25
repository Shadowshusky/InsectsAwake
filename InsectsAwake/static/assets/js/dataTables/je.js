$('#createtask').click(function () {
    taskname = $('#taskname').val();
    if (!taskname) {
        alert("任务名不可为空！", "", "error");
    }
    plan = $('#form-field-plan').val();
    target_text = $('#target-text').val();
    // if (!target_text) {
    //     alert("扫描对象不可为空！", "", "error");
    // }
    plugin_text = $('#form-field-plugin').val().join(",");
    // if (!plugin_text) {
    //     alert("请选择扫描插件！", "", "error");
    // }
    //
    $.post('/newtask', {
        taskname: taskname,
        plan: plan,
        target_text: target_text,
        plugin_text: plugin_text,
    }, function (e) {
        if (e == 'success') {
            alert("建立成功", '', "success");
            location.href = "/tasks";
        } else {
            alert("创建失败", "请检查数据是否完整或是否选择扫描对象!", "error")
        }
    })
});