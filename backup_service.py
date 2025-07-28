import win32serviceutil
import win32service
import win32event
import servicemanager
import os
import sys
import time
import json
import logging
import threading

BACKUP_JOBS_FILE = 'backup_jobs.json'
SERVICE_LOG_FILE = 'backup_service.log'
STATE_FILE = 'backup_service_state.json'

class BackupService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'BackupService'
    _svc_display_name_ = 'Backup Service for File Backups'
    _svc_description_ = 'Runs backup jobs in the background, reading from a job queue.'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.stop_requested = False
        self.logger = self._setup_logger()
        self.state = self._load_state()
        self.worker_thread = None

    def _setup_logger(self):
        logger = logging.getLogger('BackupService')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(SERVICE_LOG_FILE)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f'Failed to load state: {e}')
        return {"last_completed_job": None}

    def _save_state(self):
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(self.state, f)
        except Exception as e:
            self.logger.error(f'Failed to save state: {e}')

    def SvcStop(self):
        self.logger.info('Service stop requested.')
        self.stop_requested = True
        win32event.SetEvent(self.hWaitStop)
        if self.worker_thread:
            self.worker_thread.join(timeout=10)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.logger.info('Service started.')
        self.worker_thread = threading.Thread(target=self.main)
        self.worker_thread.start()
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        self.logger.info('Service stopped.')

    def main(self):
        while not self.stop_requested:
            jobs = self._read_jobs()
            for idx, job in enumerate(jobs):
                if self.stop_requested:
                    break
                # Check if job already completed
                if self.state.get('last_completed_job') == idx:
                    continue
                self.logger.info(f'Starting backup job {idx+1}: {job}')
                try:
                    self._run_backup_job(job)
                    self.state['last_completed_job'] = idx
                    self._save_state()
                    self.logger.info(f'Completed backup job {idx+1}')
                except Exception as e:
                    self.logger.error(f'Error running backup job {idx+1}: {e}')
            # Sleep before checking for new jobs
            for _ in range(60):
                if self.stop_requested:
                    break
                time.sleep(1)

    def _read_jobs(self):
        if not os.path.exists(BACKUP_JOBS_FILE):
            self.logger.warning(f'Job queue file {BACKUP_JOBS_FILE} not found.')
            return []
        try:
            with open(BACKUP_JOBS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f'Failed to read job queue: {e}')
            return []

    def _run_backup_job(self, job):
        # Stub: Replace this with your actual backup logic (e.g., call Robocopy)
        source = job.get('source')
        destination = job.get('destination')
        options = job.get('options', '')
        self.logger.info(f'Would run backup: {source} -> {destination} {options}')
        # Simulate backup duration
        time.sleep(5)
        # To integrate real logic, import your backup function or use subprocess to call Robocopy

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        # For debugging: run main loop in foreground
        service = BackupService([BackupService._svc_name_])
        service.main()
    else:
        # Let win32serviceutil handle all other cases (including install, start, stop, and service manager calls)
        win32serviceutil.HandleCommandLine(BackupService)