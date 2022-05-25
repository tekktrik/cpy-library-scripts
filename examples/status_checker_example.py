from status_checker import check_build_statuses, save_build_statuses

failed, errored = check_build_statuses(user="tekktrik", debug=True)
save_build_statuses(failed, errored)
