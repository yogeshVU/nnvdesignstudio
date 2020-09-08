
def setupJob(projectInfo, folder_path, param_filename):

    # logger.info("folder_path: {0}".format(folder_path))
    # logger.info("param_filename: {0} ".format(param_filename))
    # logger.info("projectInfo {0}".format(projectInfo))
    print("Setup Job")
    return runJob(runtime='docker',folder_path=folder_path,job_params=param_filename)

def runJob(runtime,folder_path,job_params):
    # logger.info("Run Job....")
    print("Run Job...")
    return
