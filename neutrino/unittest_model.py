#!/usr/bin/python38
import unittest


class unittest_stock(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    @unittest.skip('Pass')
    def test_database_connect(self):
        from libmysql_utils.mysql8 import mysqlBase, GLOBAL_HEADER
        event = mysqlBase(GLOBAL_HEADER)
        print(GLOBAL_HEADER)
        print(event._version())

    @unittest.skip('Pass')
    def test_task(self):
        from libtask.task_manager import taskManager
        from dev_global.env import TASK_FILE
        event = taskManager(taskfile=TASK_FILE, task_manager_name='neutrino')
        event.task_report()
        print(event.task_solver.func_list)
        event._update_task_list()
        event._task_list = event.check_task_list()
        for task in event._task_list:
            print(task.flag)

    def test_task_manage(self):
        from libmysql_utils.mysql8 import mysqlBase, TASK_HEADER
        from libtask.task_manager import taskManager, taskConfig
        from apscheduler.executors.pool import ThreadPoolExecutor
        from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
        from dev_global.env import TASK_FILE
        mysql = mysqlBase(TASK_HEADER)
        jobstores = {
            'default': SQLAlchemyJobStore(tablename="test_task_sched", engine=mysql.engine)
            }
        task_config = taskConfig()
        event = taskManager(
            task_config=task_config,
            taskfile=TASK_FILE,
            task_manager_name='test',
            jobstores=jobstores,
            executors={'default': ThreadPoolExecutor(20)},
            job_defaults={'max_instance': 5})
        event.start()
        event._task_list = event.check_task_list()
        for task in event._task_list:
            print(task)
        event.task_manage(event._task_list)


if __name__ == "__main__":
    unittest.main()
