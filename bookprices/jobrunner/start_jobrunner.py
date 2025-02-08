from bookprices.jobrunner.job.base import JobBase, JobResult, JobExitStatus
from bookprices.jobrunner.job.trim_prices import TrimPricesJob, start_job





jobs = {
    TrimPricesJob.name: start_job
}


def main():
    pass


if __name__ == "__main__":
    main()