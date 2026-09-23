def aggregate_data(data, report_period):
    """
    Формирует агрегированный отчёт по попыткам пользователей
    за указанный период.
    """
    report = {
        "period": report_period,
        "total_attempts": 0,
        "run_attempts": 0,
        "submit_attempts": 0,
        "successful_submits": 0,
        "failed_submits": 0,
        "unique_users": 0,
        "success_rate": 0,
    }

    report["total_attempts"] = len(data)

    run_attempts = 0
    for record in data:
        if record["attempt_type"] == "run":
            run_attempts += 1

    report["run_attempts"] = run_attempts

    submit_attempts = 0
    for record in data:
        if record["attempt_type"] == "submit":
            submit_attempts += 1

    report["submit_attempts"] = submit_attempts

    successful_submits = 0
    for record in data:
        if record["attempt_type"] == "submit" and record["is_correct"] is True:
            successful_submits += 1

    report["successful_submits"] = successful_submits

    failed_submits = 0
    for record in data:
        if record["attempt_type"] == "submit" and record["is_correct"] is False:
            failed_submits += 1

    report["failed_submits"] = failed_submits

    user_ids = set()
    for record in data:
        user_ids.add(record["user_id"])

    report["unique_users"] = len(user_ids)

    if submit_attempts > 0:
        report["success_rate"] = (successful_submits / submit_attempts) * 100

    return report
