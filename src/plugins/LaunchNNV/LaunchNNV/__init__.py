"""
This is where the implementation of the plugin code goes.
The LaunchNNV-class is imported from both run_plugin.py and run_debug.py
"""
import json
import os
import sys
import logging
import time
import traceback

from webgme_bindings import PluginBase
from . import NNVKeys
from pathlib import Path

# Setup a logger
from . import DockerJob

logger = logging.getLogger('LaunchNNV')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_logger(clazz):
    logger_name = clazz.__module__ + "." + clazz.__name__
    logger = logging.Logger(logger_name)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


class LaunchNNV(PluginBase):

    def __init__(self, *args, **kwargs):
        super(LaunchNNV, self).__init__(*args, **kwargs)
        self.test = False
        if "test" in kwargs:
            self.test = kwargs.get("test")

        # self.config = self.get_current_config()
        self.active_node_meta_type = None
        self.active_node_meta_type_name = None

    def main(self):
        try:
            template_parameter_map = {}
            image_file = None
            lec_file_name = None

            #
            # TEMPLATE PARAMETERS:  GET PROJECT NAME AND OWNER
            #
            project_info = self.project.get_project_info()
            logger.info(NNVKeys.template_project_name_key)
            project_name = project_info.get(NNVKeys.template_project_name_key)
            project_owner = project_info.get(NNVKeys.template_owner_name_key)

            template_parameter_map[NNVKeys.template_project_name_key] = project_name
            template_parameter_map[NNVKeys.template_owner_name_key] = project_owner

            #
            # VERIFICATION_SETUP NODE SHOULD BE ACTIVE NODE
            #
            self.active_node_meta_type = self.core.get_meta_type(self.active_node)
            self.active_node_meta_type_name = self.core.get_fully_qualified_name(self.active_node_meta_type)

            if not self.check_active_node_meta():
                raise RuntimeError("Model needs to be one of {0}".format(NNVKeys.valid_meta_type_name_set))

            verification_setup_child_node_map = self.get_child_nodes(self.active_node)

            verification_model_node_list = verification_setup_child_node_map.get(
                NNVKeys.template_lec_exec_node_meta, []
            )

            if len(verification_model_node_list) == 0:
                raise RuntimeError(
                    "No object found of meta-type \"{0}\" in meta-type object.".format(
                        NNVKeys.template_lec_exec_node_meta

                    )
                )

            if len(verification_model_node_list) > 1:
                LaunchNNV.logger.warning(
                    "More than one object of meta-type \"{0}\" found in  meta-type object.  "
                    "Using the first one.".format(
                        NNVKeys.template_lec_exec_node_meta
                    )
                )

            verification_model_node = verification_model_node_list[0]
            lec_node_path = self.core.get_pointer_path(verification_model_node, NNVKeys.template_lec_exec_node_pointer)
            lec_node = self.core.load_by_path(self.root_node, lec_node_path)
            lec_node_type = self.core.get_fully_qualified_name(self.core.get_meta_type(lec_node))
            logger.info("LEC Node Type {0}".format(lec_node_type))
            logger.info("LEC info: {0} {1}".format(self.core.get_attribute(lec_node, "name"),
                                                   self.core.get_attribute(lec_node, "model")))
            # lec_hash = self.core.get_attribute(lec_node, "model")
            # logger.info("Hash is {0}".format(lec_hash))
            # lec_file_content = self.get_file(lec_hash)
            lec_file_name = self.core.get_attribute(lec_node, "name")
            template_parameter_map[NNVKeys.template_lec_file_name_key] = lec_file_name

            modelpath = self.core.get_attribute(self.core.get_parent(lec_node),'name')


            # Dataset Parsing
            verification_dataset_node_list = verification_setup_child_node_map.get(
                NNVKeys.template_dataset_exec_node_meta, []
            )

            # if len(verification_dataset_node_list)  1:
            #     LaunchNNV.logger.warning(
            #         "More than one object of meta-type \"{0}\" found in  meta-type object.  "
            #         "Using the first one.".format(
            #             NNVKeys.template_dataset_exec_node_meta
            #         )
            #     )
            # else:
            if len(verification_dataset_node_list)>0:
                verification_dataset_node = verification_dataset_node_list[0]
                dataset_node_path = self.core.get_pointer_path(verification_dataset_node,
                                                               NNVKeys.template_dataset_exec_node_pointer)
                dataset_node = self.core.load_by_path(self.root_node, dataset_node_path)
                dataset_node_type = self.core.get_fully_qualified_name(self.core.get_meta_type(dataset_node))
                logger.info("Dataset Node Type {0}".format(dataset_node_type))
                logger.info("Dataset info: {0} {1}".format(self.core.get_attribute(dataset_node, "name"), \
                                                           self.core.get_attribute(dataset_node, "image")))
                image_file = self.core.get_attribute(dataset_node, "name")

                template_parameter_map['image'] = image_file
            # logger.info("Image Hash is {0}".format(dataset_hash))
            # image_file = self.get_file(dataset_hash)

            # if image_file == None:
            #     logger.info("no images")
            # else:
            #     logger.info("Image file is {0}".format(image_file))
            #
            # logger.info("---> Image Hash is {0}".format(dataset_hash))

            # try:
            # image_file_content = self.get_file(dataset_hash)
            # except Exception as err:
            #     msg = str(err)
            #     self.create_message(self.active_node, msg, 'error')
            #     # self.result_set_error('LaunchNNV Plugin: Error encountered.  Check result details.')
            #     # self.result_set_success(False)
            #     exit()

            # logger.info("File infor: {0}".format(lec_file_content))
            # logger.info("LEC info: {0}, {1}".format(self.core.get_attribute(lec_node,"name")), self.core.get_attribute(lec_node,"model"))

            verification_neuralnetwork_node_list = verification_setup_child_node_map.get(
                NNVKeys.template_NN_exec_node_meta, []
            )

            if len(verification_neuralnetwork_node_list) == 0:
                raise RuntimeError(
                    "No object found of meta-type \"{0}\" in meta-type object.".format(
                        NNVKeys.template_NN_exec_node_meta

                    )
                )
            verification_neuralnetwork_node = verification_neuralnetwork_node_list[0]

            neuralnetwork_node_path = self.core.get_pointer_path(verification_neuralnetwork_node,
                                                                 NNVKeys.template_NN_exec_node_pointer)
            neuralnetwork_node = self.core.load_by_path(self.root_node, neuralnetwork_node_path)

            logger.info("lec_path {0} and neural_network_path {1}".format(lec_node_path, neuralnetwork_node_path))
            neuralnetwork_type = self.core.get_fully_qualified_name(self.core.get_meta_type(neuralnetwork_node))
            logger.info("Neural Network Type {0}".format(neuralnetwork_type))

            template_parameter_map[NNVKeys.template_NN_node_base_meta] = neuralnetwork_type

            if neuralnetwork_type in NNVKeys.template_NN_node_valid_meta:
                logger.info("Valid Neural Network Controller {0}".format(neuralnetwork_type))
                for ikey in NNVKeys.template_NN_param[neuralnetwork_type]:
                    template_parameter_map[ikey] = self.core.get_attribute(neuralnetwork_node, ikey)
                    logger.info("values of template:  {0} --> {1}".format(ikey, template_parameter_map[ikey]))

            from pprint import pformat
            logger.info(pformat(template_parameter_map))

            seconds_since_epoch = int(time.time())
            specific_directory_path = Path(NNVKeys.output_directory_name, str(seconds_since_epoch))
            specific_directory_path.mkdir(parents=True)
            template_parameter_file = Path(
                specific_directory_path, NNVKeys.template_parameter_file_name
            )

            lec_model_file_path = Path(
                specific_directory_path, lec_file_name
            )

            if image_file is not None:
                image_file_output_path = Path(
                    specific_directory_path, image_file
                )
                import shutil
                image_input_path = Path(NNVKeys.upload_artifact_directory, project_owner, project_name,modelpath, image_file)

                try:
                    shutil.copy2(str(image_input_path), str(image_file_output_path))  # complete target filename given
                except Exception as err1:
                    msg = str(err1)
                    LaunchNNV.logger.info('exception ' + msg)
                    traceback_msg = traceback.format_exc()
                    LaunchNNV.logger.info(traceback_msg)
                    sys_exec_info_msg = sys.exc_info()[2]
                    LaunchNNV.logger.info(sys_exec_info_msg)
                    self.create_message(self.active_node, msg, 'error')
                    self.create_message(self.active_node, traceback_msg, 'error')
                    self.create_message(self.active_node, sys_exec_info_msg, 'error')
                    # self.result_set_error('LaunchNNV Plugin: Error encountered.  Check result details.')
                    # self.result_set_success(False)
                    exit()

            if lec_file_name is not None:
                import shutil
                lec_model_input_path = Path(NNVKeys.upload_artifact_directory, project_owner, project_name,modelpath, lec_file_name)
                logger.info("LEC_FILE_PATH:{0} , LEC_OUTPUT_PATH: {1}".format(lec_model_input_path, lec_model_file_path))

                try:
                    shutil.copy2(str(lec_model_input_path), str(lec_model_file_path))  # complete target filename given
                except Exception as err1:
                    msg = str(err1)
                    LaunchNNV.logger.info('exception ' + msg)
                    traceback_msg = traceback.format_exc()
                    LaunchNNV.logger.info(traceback_msg)
                    sys_exec_info_msg = sys.exc_info()[2]
                    LaunchNNV.logger.info(sys_exec_info_msg)
                    self.create_message(self.active_node, msg, 'error')
                    self.create_message(self.active_node, traceback_msg, 'error')
                    self.create_message(self.active_node, sys_exec_info_msg, 'error')
                    # self.result_set_error('LaunchNNV Plugin: Error encountered.  Check result details.')
                    # self.result_set_success(False)
                    exit()

            # with lec_model_file.open("w") as lec_model_file_fp:
            #     try:
            #         lec_model_file_fp.write(lec_file_content)
            #     except Exception as err1:
            #         msg = str(err1)
            #         LaunchNNV.logger.info('exception ' + msg)
            #         traceback_msg = traceback.format_exc()
            #         LaunchNNV.logger.info(traceback_msg)
            #         sys_exec_info_msg = sys.exc_info()[2]
            #         LaunchNNV.logger.info(sys_exec_info_msg)
            #         self.create_message(self.active_node, msg, 'error')
            #         self.create_message(self.active_node, traceback_msg, 'error')
            #         self.create_message(self.active_node, sys_exec_info_msg, 'error')
            #         # self.result_set_error('LaunchNNV Plugin: Error encountered.  Check result details.')
            #         # self.result_set_success(False)
            #         exit()

            with template_parameter_file.open("w", encoding="utf-8") as template_parameter_file_fp:
                try:
                    json.dump(template_parameter_map, template_parameter_file_fp, indent=4,
                                             sort_keys=True, ensure_ascii=False)
                    # if isinstance(my_json_str, str):
                    #     my_json_str = my_json_str.decode("utf-8")
                    # template_parameter_file_fp.write(my_json_str)
                except Exception as err1:
                    msg = str(err1)
                    LaunchNNV.logger.info('exception ' + msg)
                    traceback_msg = traceback.format_exc()
                    LaunchNNV.logger.info(traceback_msg)
                    sys_exec_info_msg = sys.exc_info()[2]
                    LaunchNNV.logger.info(sys_exec_info_msg)
                    self.create_message(self.active_node, msg, 'error')
                    self.create_message(self.active_node, traceback_msg, 'error')
                    self.create_message(self.active_node, sys_exec_info_msg, 'error')
                    # self.result_set_error('LaunchNNV Plugin: Error encountered.  Check result details.')
                    # self.result_set_success(False)
                    exit()

            # logger.info(self.get_current_config())
            # config_name = self.get_current_config()+"_"+str(seconds_since_epoch)
            logger.info("Now calling the DockerJob....")
            run_result = DockerJob.setupJob(self.project.get_project_info(), specific_directory_path, template_parameter_file)
            logger.info(run_result)
            # self.add_file('log.txt', str(run_result))
            # self.add_file('log2.txt', str(run_result))

            # hash = self.add_artifact('ResultArtifact', {'log.txt': str(run_result)})

            import zipfile
            z = zipfile.ZipFile(str(specific_directory_path)+ '/result.zip', "w")

            import glob
            svg_files = str(specific_directory_path) + "/*.svg"
            print(svg_files)
            try:
                for filename in glob.glob(svg_files):
                    base = os.path.basename(filename)
                    print(base)
                    binary_file =  open(filename, 'r')
                    binary_content = binary_file.read()
                    bin_hash = self.add_file(str(filename), binary_content)
                    z.write(filename,arcname=base)

                    # Write to  the zip file....
                z.close()
                binary_file = open(str(specific_directory_path)+ '/result.zip', 'r')
                binary_content = binary_file.read()
                bin_hash = self.add_file(str(specific_directory_path)+ '/result.zip', binary_content)
                # hash_zip = self.add_artifact('ResultArtifact', {str(specific_directory_path)+ '/result.zip': binary_content})
                # binary_file = open(str(specific_directory_path)+ '/template_parameters.json', 'r')
                # binary_content = binary_file.read()
                # bin_hash = self.add_file(str(specific_directory_path)+ '/template_parameters.json', binary_content)
            except Exception as err:
                print(err)

            # retrieved_content = self.get_bin_file(hash_zip)
            # if hash_zip !=retrieved_content:
            #     print("mismatch...")
            # else:
            #     print("They match....")

            self.add_file('log.txt', str(run_result))

            #
        ## Next we pass this information to the matlab docker runner....
        # self.result_set_success(True)
        except Exception as err:
            msg = str(err)
            self.create_message(self.active_node, msg, 'error')
            # self.result_set_error('LaunchNNV Plugin: Error encountered.  Check result details.')
            # self.result_set_success(False)
            exit()

    def check_active_node_meta(self):
        return self.active_node_meta_type_name in NNVKeys.valid_meta_type_name_set

    def get_child_nodes(self, parent_node):

        child_node_list = self.core.load_sub_tree(parent_node)
        child_node_map = {}
        for child_node in child_node_list:
            if not child_node:
                continue

            child_node_meta_type = self.core.get_meta_type(child_node)
            child_node_meta_type_name = self.core.get_fully_qualified_name(child_node_meta_type)
            child_node_list = child_node_map.get(child_node_meta_type_name, [])
            child_node_list.append(child_node)
            child_node_map[child_node_meta_type_name] = child_node_list

        return child_node_map

    def get_model_node_path(self, node, retval=Path()):
        if node is None:
            return retval

        node_name = self.core.get_fully_qualified_name(node)
        if node_name == NNVKeys.template_root_node_name:
            return Path('/', retval)

        return self.get_model_node_path(
            self.core.get_parent(node), Path(node_name, retval)
        )

    def parseExperiments(self, node):
        print(self.core.get_attribute(node, 'name'))


LaunchNNV.logger = get_logger(LaunchNNV)
