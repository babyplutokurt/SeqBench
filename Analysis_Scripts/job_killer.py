import subprocess


def list_user_jobs(username):
    """
    List all jobs for the specified user.

    Parameters:
    username (str): The username to list jobs for.

    Returns:
    list: A list of job IDs.
    """
    try:
        # Run the qstat command and capture the output
        result = subprocess.run(['qstat', '-u', username], capture_output=True, text=True, check=True)

        # Split the output into lines
        lines = result.stdout.split('\n')

        # Extract job IDs (assuming job ID is the first field in the output)
        job_ids = [line.split()[0] for line in lines if line and line.split()[0].isdigit()]

        return job_ids
    except subprocess.CalledProcessError as e:
        print(f"Error listing jobs for user {username}: {e}")
        return []


def delete_jobs(job_ids):
    """
    Delete the jobs with the specified job IDs.

    Parameters:
    job_ids (list): A list of job IDs to delete.
    """
    for job_id in job_ids:
        try:
            # Run the qdel command to delete the job
            subprocess.run(['qdel', job_id], check=True)
            print(f"Deleted job {job_id}")
        except subprocess.CalledProcessError as e:
            print(f"Error deleting job {job_id}: {e}")


if __name__ == "__main__":
    # Replace 'your_username' with the actual username
    username = 'tus53997'

    # List the user's jobs
    job_ids = list_user_jobs(username)


    # Delete the user's jobs
    delete_jobs(job_ids)
