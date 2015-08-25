import sys
from behave import when, then
from chronos import ChronosJob

sys.path.append('../')
from paasta_tools.utils import _run
from paasta_tools import chronos_tools

@when('I have no jobs listed in config')
def write_empty_config(context):
    pass

@when('I launch "{num_jobs}" chronos jobs')
def launch_jobs(context, num_jobs):
    client = context.chronos_client
    jobs = [{
        'async': False,
        'command': 'echo 1',
        'epsilon': 'PT15M',
        'name': 'test_chronos_job-%d' % job,
        'owner': '',
        'disabled': True,
        'schedule': 'R/2014-01-01T00:00:00Z/PT60M',
    } for job in range(0,int(num_jobs))]
    context.job_names = [job['name'] for job in jobs]
    for job in jobs:
        try:
            client.add(job)
        except Exception:
            print 'Error creating test job'
            raise

@then('cleanup_chronos_jobs exits with return code "{expected_return_code}" and the correct output')
def check_cleanup_chronos_jobs_output(context, expected_return_code):
    cmd = '../paasta_tools/cleanup_chronos_jobs.py'
    (exit_code, output) = _run(cmd)
    print 'Got exitcode %s with output:\n%s' % (exit_code, output)
    print context.job_names

    assert exit_code == int(expected_return_code)
    assert "Successfully Removed:" in output
    for job in context.job_names:
        assert '  %s' % job in output

@then('the jobs are no longer listed in chronos')
def check_jobs_missing(context):
    jobs = context.chronos_client.list()
    running_job_names = [job['name'] for job in jobs]
    assert all([job_name not in running_job_names for job_name in context.job_names])
