
def setupJob(projectInfo, folder_path, param_filename) -> str:

    # logger.info("folder_path: {0}".format(folder_path))
    # logger.info("param_filename: {0} ".format(param_filename))
    # logger.info("projectInfo {0}".format(projectInfo))
    print("Setup Job")
    return runJob(runtime='docker',folder_path=folder_path,job_params=param_filename)

def runJob(runtime,folder_path,job_params):
    output_log = ""
    try:
        import subprocess
        venv_python = '/home/ubuntu/yogesh/python-tut/venv/bin/python'
        args = [venv_python, '/home/ubuntu/yogesh/python-tut/NNVEntry.py', '--json', str(job_params), '--inputdir', str(folder_path)]
        process = subprocess.Popen(args, stdout=subprocess.PIPE,
               stderr=subprocess.STDOUT,universal_newlines=True)
        while True:
            output = process.stdout.readline()

            # print(output.strip())
            output_log = output_log + output + '\n'
            # logger.info(output.strip())
            # Do something else
            return_code = process.poll()
            if return_code is not None:
                # logger.info('RETURN CODE: {0}'.format( return_code))
                print('Return Code :',return_code)
                # Process has finished, read rest of the output

                # output_log = output_log + process.stdout.readlines()

                for output in process.stdout.readlines():
                    # logger.info(output.strip())
                    # print(output.strip())
                    output_log = output_log + output.strip() + '\n'
                break

    except Exception as esp:
        print(esp)
    return output_log
