"""
This is where the implementation of the plugin code goes.
The LaunchNNV-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
from webgme_bindings import PluginBase
from . import NNVKeys
from pathlib import Path

# Setup a logger
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

            #
            # TEMPLATE PARAMETERS:  GET PROJECT NAME AND OWNER
            #
            project_info = self.project.get_project_info()
            logger.info(NNVKeys.template_project_name_key)
            project_name = project_info.get(NNVKeys.template_project_name_key)
            project_owner = project_info.get(NNVKeys.template_project_name_key)

            template_parameter_map[NNVKeys.template_project_name_key] = project_name
            template_parameter_map[NNVKeys.template_owner_name_key] = project_owner

            #
            # VERIFICATION_SETUP NODE SHOULD BE ACTIVE NODE
            #
            self.active_node_meta_type = self.core.get_meta_type(self.active_node)
            self.active_node_meta_type_name = self.core.get_fully_qualified_name(self.active_node_meta_type)

            if not self.check_active_node_meta():
                raise RuntimeError("Model needs to be one of {0}".format(NNVKeys.valid_meta_type_name_set))

            #
            #  GET CHILD VERIFICATION_MODEL NODE OF VERIFICATION_SETUP NODE
            #
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
            # # GET NODE OF LEC POINTED TO BY LED MODEL NODE
            # #
            lec_node_path = self.core.get_pointer_path(verification_model_node,NNVKeys.template_lec_exec_node_pointer)
            lec_node = self.core.load_by_path(self.root_node,lec_node_path)
            neuralnetwork_node_path = self.core.get_pointer_path(verification_neuralnetwork_node, NNVKeys.template_NN_exec_node_pointer)
            neuralnetwork_node = self.core.load_by_path(self.root_node, neuralnetwork_node_path)

            logger.info("lec_path {0} and neural_network_path {1}".format(lec_node_path,neuralnetwork_node_path))
            neuralnetwork_type = self.core.get_fully_qualified_name(self.core.get_meta_type(neuralnetwork_node))
            logger.info("Neural Network Type {0}".format(self.core.get_fully_qualified_name(neuralnetwork_type)))

            if neuralnetwork_type

            #
            # #
            # # TEMPLATE PARAMETERS:  LEC NODE PATH AND ID
            # #
            # template_parameter_map[RobustnessKeys.template_lec_node_id_key] = lec_path
            # template_parameter_map[RobustnessKeys.template_lec_node_path_key] = str(self.get_model_node_path(lec_node))

            # # MAKE SURE ATTACK-PARAMETER SPECIFIED
            # if RobustnessKeys.attack_parameter_key not in parameter_map:
            #     raise RuntimeError("\"{0}\" object must have \"{1}\" parameter.".format(
            #         LaunchVerification.alcmeta_verification_model_meta_name,
            #         RobustnessKeys.attack_parameter_key
            #     ))
            #
            # attack_type = parameter_map.get(RobustnessKeys.attack_parameter_key)
            # if attack_type not in RobustnessKeys.attack_map.keys():
            #     raise RuntimeError("Invalid attack type \"{0}\":  must be one of \"{1}\".".format(
            #         attack_type, RobustnessKeys.attack_map.keys()
            #     ))
            #
            # #
            # # GET NAMES OF ALL REQUIRED PARAMETERS
            # #
            # extra_parameter_set = RobustnessKeys.attack_map \
            #     .get(attack_type) \
            #     .get(RobustnessKeys.required_parameters_key)
            #
            # required_parameter_name_set = LaunchVerification.parameter_name_set.union(
            #     extra_parameter_set
            # )
            #
            # #
            # # DELETE UNNECESSARY PARAMETERS
            # #
            # parameter_map_key_set = set(parameter_map.keys())
            # unnecessary_parameter_name_set = parameter_map_key_set.difference(required_parameter_name_set)
            # for key in unnecessary_parameter_name_set:
            #     del parameter_map[key]
            #
            # #
            # # MAKE SURE ALL REQUIRED PARAMETERS ARE PRESENT
            # #
            # parameter_map_key_set = set(parameter_map.keys())
            # missing_parameter_set = required_parameter_name_set.difference(parameter_map_key_set)
            #
            # if len(missing_parameter_set) != 0:
            #     raise RuntimeError("Missing parameters \"{0}\"for attack type \"{1}\".".format(
            #         missing_parameter_set, attack_type
            #     ))
            #
            # #
            # # GET PERCEPTION LEC MODEL DIRECTORY
            # #
            #
            # # GET LEC MODEL NODE
            # lec_model_node_list = verification_model_child_node_map.get(LaunchVerification.alcmeta_lec_model_meta_name)
            # if len(lec_model_node_list) == 0:
            #     raise RuntimeError("At least one \"{0}\" object must be in \"{1}\" model".format(
            #         LaunchVerification.alcmeta_lec_model_meta_name,
            #         LaunchVerification.alcmeta_verification_model_meta_name
            #     ))
            # if len(lec_model_node_list) > 1:
            #     LaunchVerification.logger.warning(
            #         "More than one \"{0}\" object found in \"{1}\" model.  Using the first".format(
            #             LaunchVerification.alcmeta_lec_model_meta_name,
            #             LaunchVerification.alcmeta_verification_model_meta_name
            #         )
            #     )
            #
            # lec_model_node = lec_model_node_list[0]
            #
            # #
            # # TEMPLATE PARAMETERS:  LEC MODEL NODE PATH AND ID
            # #
            # template_parameter_map[RobustnessKeys.template_lec_node_reference_path_key] = \
            #     str(self.get_model_node_path(lec_model_node))
            # template_parameter_map[RobustnessKeys.template_lec_node_reference_id_key] = \
            #     self.core.get_path(lec_model_node)
            #
            # #
            # # GET NODE OF LEC POINTED TO BY LED MODEL NODE
            # #
            # lec_path = self.core.get_pointer_path(lec_model_node, LaunchVerification.alcmeta_lec_model_pointer_name)
            # lec_node = self.core.load_by_path(self.root_node, lec_path)
            #
            # #
            # # TEMPLATE PARAMETERS:  LEC NODE PATH AND ID
            # #
            # template_parameter_map[RobustnessKeys.template_lec_node_id_key] = lec_path
            # template_parameter_map[RobustnessKeys.template_lec_node_path_key] = str(self.get_model_node_path(lec_node))
            #
            # # GET LEC MODEL DIRECTORY
            # lec_info_map_str = self.core.get_attribute(
            #     lec_node, LaunchVerification.alcmeta_set_member_attribute_name
            # )
            # lec_info_map = json.loads(lec_info_map_str)
            # lec_directory = lec_info_map.get(LaunchVerification.data_info_map_directory_key)
            # lec_directory_path = Path(lec_directory)
            #
            # # GET THE LEC FILE
            # network_directory_path = Path(lec_directory_path, LaunchVerification.network_directory_name)
            # mat_file_list = sorted(network_directory_path.glob("*.mat"))
            #
            # if len(mat_file_list) == 0:
            #     raise RuntimeError(
            #         "lec directory \"{0}\" must contain at least one mat-file"
            #         " (that contains a neural network).".format(network_directory_path)
            #     )
            # mat_file = mat_file_list[0].absolute()
            #
            # #
            # # TEMPLATE PARAMETERS:  LEC DIRECTORY PATH, LEC NETWORK DIRECTORY PATH, LEC MAT-FILE NAME
            # #
            # template_parameter_map[RobustnessKeys.template_lec_parent_directory_path_key] = \
            #     str(lec_directory_path)
            # template_parameter_map[RobustnessKeys.template_lec_directory_path_key] = str(network_directory_path)
            # template_parameter_map[RobustnessKeys.template_lec_file_name_key] = str(mat_file.name)
            #
            # if len(mat_file_list) > 1:
            #     LaunchNNV.logger.warning(
            #         "More than 1 mat-file found in \"{0}\" directory.  Using \"{1}\"".format(
            #             network_directory_path, mat_file.name
            #         )
            #     )
            #
            # #
            # # GET TEST-DATA DIRECTORIES
            # #
            #
            # # GET EVAL_DATA NODE
            # if LaunchNNV.alcmeta_eval_data_meta_name not in verification_model_child_node_map:
            #     raise RuntimeError("\"{0}\" object must be in \"{1}\" model".format(
            #         LaunchVerification.alcmeta_eval_data_meta_name,
            #         LaunchVerification.alcmeta_verification_model_meta_name
            #     ))
            #
            # eval_data_node_list = verification_model_child_node_map.get(LaunchVerification.alcmeta_eval_data_meta_name)
            # if len(eval_data_node_list) == 0:
            #     raise RuntimeError("At least one \"{0}\" object must be in \"{1}\" model".format(
            #         LaunchNNV.alcmeta_eval_data_meta_name,
            #         LaunchNNV.alcmeta_verification_model_meta_name
            #     ))
            # if len(eval_data_node_list) > 1:
            #     LaunchNNV.logger.warning(
            #         "More than one \"{0}\" object found in \"{1}\" model.  Using the first".format(
            #             LaunchNNV.alcmeta_eval_data_meta_name,
            #             LaunchNNV.alcmeta_verification_model_meta_name
            #         )
            #     )
            #
            # eval_data_node = eval_data_node_list[0]
            #
            # #
            # # TEMPLATE PARAMETERS:  EVALDATA NODE PATH AND ID
            # #
            # template_parameter_map[RobustnessKeys.template_eval_data_node_path_key] = \
            #     str(self.get_model_node_path(eval_data_node))
            # template_parameter_map[RobustnessKeys.template_eval_data_node_id_key] = \
            #     self.core.get_path(eval_data_node)
            #
            # # GET "LaunchVerification.alcmeta_eval_data_set_name" SET MEMBER VALUE
            # # -- LIST OF DATACOLLECTION RESULT NODE PATHS
            # set_member_list = self.core.get_member_paths(eval_data_node, LaunchNNV.alcmeta_eval_data_set_name)
            # if len(set_member_list) == 0:
            #     raise RuntimeError("\"{0}\" object must contain \"{1}\" set with at least 1 item.".format(
            #         LaunchNNV.alcmeta_eval_data_meta_name, LaunchVerification.alcmeta_eval_data_set_name
            #     ))
            #
            # # GET (STRING) PATHS OF DIRECTORIES CONTAINING TEST DATA
            # test_data_directory_list = []
            # for set_member in set_member_list:
            #     set_member_node = self.core.load_by_path(self.root_node, set_member)
            #     data_info_map_str = self.core.get_attribute(
            #         set_member_node, LaunchVerification.alcmeta_set_member_attribute_name
            #     )
            #     data_info_map = json.loads(data_info_map_str)
            #     test_data_directory_list.append(
            #         data_info_map.get(LaunchVerification.data_info_map_directory_key)
            #     )
            #
            # if len(test_data_directory_list) == 0:
            #     raise RuntimeError(
            #         "\"{0}\" object must contain at least one directory with category-named"
            #         " subdirectories and test images of a given category under the corresponding category-named"
            #         " directory."
            #     )
            #
            # #
            # # TEMPLATE PARAMETERS:  TEST-DATA-DIRECTORY-LIST AND PARAMETER MAP
            # #
            # template_parameter_map[RobustnessKeys.template_test_data_directory_list_key] = test_data_directory_list
            # template_parameter_map[RobustnessKeys.template_parameter_map_key] = parameter_map
            #
            # #
            # # GET DATASET SCRIPT FOR EXTRACTING TRAINING/TESTING DATA IMAGES, CATEGORY NAMES, CATEGORY VALUES
            # #
            # lec_dataset_script_text = self.core.get_attribute(
            #     lec_model_node, LaunchVerification.alcmeta_lec_model_dataset_name
            # )
            # template_parameter_map[RobustnessKeys.template_dataset_key] = lec_dataset_script_text
            #
            # project_jupyter_notebook_directory_path = Path(
            #     lec_directory_path, RobustnessKeys.notebooks_directory_name
            # )
            # seconds_since_epoch = int(time.time())
            # specific_notebook_directory_path = Path(project_jupyter_notebook_directory_path, str(seconds_since_epoch))
            # specific_notebook_directory_path.mkdir(parents=True)
            #
            # template_parameter_map[RobustnessKeys.template_specific_notebook_directory_key] = \
            #     str(specific_notebook_directory_path)
            #
            # template_parameter_file = Path(
            #     specific_notebook_directory_path, RobustnessKeys.template_parameter_file_name
            # )
            # with template_parameter_file.open("w") as template_parameter_file_fp:
            #     json.dump(template_parameter_map, template_parameter_file_fp, indent=4, sort_keys=True)

            #
            # EXECUTE SLURM HERE
            #

        except Exception as err:
            msg = str(err)
            self.create_message(self.active_node, msg, 'error')
            self.result_set_error('LaunchNNV Plugin: Error encountered.  Check result details.')
            self.result_set_success(False)
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
