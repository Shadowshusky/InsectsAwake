$('#updatetask').click(function () {
    task_name = $('#task_name').val();
    if (!task_name) {
        alert("任务名不可为空！");
    }
    plan = $('#form-field-plan').val();
    target_text = $('#scan_target_list').val();
    task_id = $('#task_id').val();
    $.post('/task-edit', {
        task_name: task_name,
        plan: plan,
        target_text: target_text,
        task_id: task_id,
    }, function (response) {
        if (response == 'success') {
            alert("更新成功");
            location.href = "/task-management";
        } else {
            alert("更新失败");
        }
    })
});