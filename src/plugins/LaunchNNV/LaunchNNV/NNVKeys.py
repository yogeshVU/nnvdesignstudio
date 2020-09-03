template_owner_name_key = "owner"
template_project_name_key = "name"
template_root_node_name = "Root"

template_experiment_node_meta = "ExperimentIndex"
template_lec_node_meta = "LEC"
template_lec_node_model_blob ="model"
template_lec_exec_node_meta = "LECExec"
template_lec_exec_node_pointer = "LEC"
template_lec_file_name_key = "LEC_file_name"


template_NN_exec_node_meta = "NNModel"
template_NN_exec_node_pointer = "NN"

template_NN_node_base_meta = "NNType"
template_NN_node_valid_meta = {
    "CNN", "FFNN", "DiscreteLinearNNCS","ContinuousLinearNNCS", "DiscreteNonLinearNNCS", "ContinuousNonLinearNNCS"
}

template_CNN_attack_key = "attack"
template_CNN_delta_key = "delta"
template_CNN_target_key = "im_target"
template_CNN_mean_key = "mean"
template_CNN_pixels_key = "pixels"
template_CNN_reachability_method_key = "reach-method"
template_CNN_std_delta_key = "std"
template_CNN_threshold_key = "threshold"


template_FFNN_halfspace_matrix_key = "HalfSpace-matrix"
template_FFNN_halfspace_vector_key = "HalfSpace-vector"
template_FFNN_lb_key= "lb"
template_FFNN_ub_key  = "ub"
template_FFNN_reachability_key = "reach"
template_FFNN_verification_key  = "verify"
template_FFNN_reachability_method_key = "reach-method"


template_NNCS_halfspace_matrix_key = "HalfSpace-matrix"
template_NNCS_halfspace_vector_key = "HalfSpace-vector"
template_NNCS_lb_key = "lb"
template_NNCS_ub_key = "ub"
template_NNCS_reachability_key = "reach"
template_NNCS_cores_key = "cores"
template_NNCS_steps = "steps"
template_NNCS_lb_refinput_key = "lb-refInput"
template_NNCS_ub_refinput_key= "ub-refInput"
template_NNCS_verification_key = "verify"
template_NNCS_reach_method_key = "reach-method"

template_NNCS_LinearSys_A_key = "A"
template_NNCS_LinearSys_B_key ="B"
template_NNCS_LinearSys_C_key ="C"
template_NNCS_LinearSys_D_key = "D"
template_NNCS_LinearSys_Ts_key  = "Ts"
template_NNCS_LinearSys_Cont_reachable_steps_key = "reachable-steps"

template_NNCS_NonLinearSys_filename_key = "file"
template_NNCS_NonLinearSys_func_key = "function"
template_NNCS_NonLinearSys_Cont_reachable_steps_key = "reachable-steps"








template_parameter_map_key = "parameter_map"

template_mean_key = "mean"
template_results_file_name_key = "results_file_name"
template_standard_deviation_key = "standard_deviation"
template_test_data_directory_list_key = "test_data_directory_list"
template_verification_node_id_key = "verification_node_id"
template_verification_node_path_key = "verification_node_path"

attack_parameter_key = "attack"
delta_parameter_key = "delta"
method_parameter_key = "method"
noise_parameter_key = "noise"
pixels_parameter_key = "pixels"
threshold_parameter_key = "threshold"

brightening_attack_type_name = "brightening"
darkening_attack_type_name = "darkening"
random_noise_attack_type_name = "random_noise"

required_parameters_key = "required_parameters"
perturbation_function_name_key = "perturbation_function_name"

attack_map = {
    brightening_attack_type_name: {
        required_parameters_key: {delta_parameter_key, threshold_parameter_key},
        perturbation_function_name_key: "perturbBrightening"
    },
    darkening_attack_type_name: {
        required_parameters_key: {delta_parameter_key, threshold_parameter_key},
        perturbation_function_name_key: "perturbDarkening"
    },
    random_noise_attack_type_name: {
        required_parameters_key: {noise_parameter_key, pixels_parameter_key},
        perturbation_function_name_key: "perturbRandomNoise"
    }
}

image_path_key = "image_path"
category_name_key = "category_name"
category_number_key = "category_number"
result_key = "result"

template_parameter_file_name = "template_parameters.json"
notebooks_directory_name = "notebooks"

valid_meta_type_name_set = {
    "ExperimentIndex",

}
