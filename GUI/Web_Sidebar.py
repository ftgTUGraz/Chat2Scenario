"""
Author: Yongqi Zhao
Date Created: 2023-12-14
Copy Right: TU Graz FTG ADAS Group
Email: yongqi.zhao@tugraz.at
"""
import streamlit as st
import pandas as pd
import ast

# Create sidebar
def sidebar():
    """
    Construct sidebar of website

    Parameters:
    -------
    Inputs:
        None
    Returns:
        dataset_option (str): selected dataset ['highD', 'inD', 'roundD', 'exitD', 'AD4CHE'] 
        option_metric (str): metric clssificationss belonging to ['Acceleration-Scale', 'Distance-Scale', 'Jerk-Scale', 'Time-Scale', 'Velocity-Scale']
        suboption_metric (str): concrete metric to search scenario in the dataset e.g., "Time To Collision (TTC)"
        dataset_load (str): path of uploaded dataset 
        metric_threshold (tuple): two floats representing "maximum value" and "minimum value"
    -------
    """
    with st.sidebar:
        st.title("Preferences")
        st.subheader(":gear: Parameter setting")

        # 1. Select Dataset
        st.markdown(
        '<style>'
        'div.stRadio > div { background-color: #FFFFFF; padding: 10px; border-radius: 5px; margin-bottom: 10px; }'
        '</style>',
        unsafe_allow_html=True
        )
        dataset_option = st.sidebar.radio(":mag: Select dataset", ['highD', 'inD', 'roundD', 'exitD', 'uniD', 'AD4CHE'])


        # 2. Upload Dataset
        dataset_load = st.sidebar.file_uploader(":file_folder: Upload dataset", type=["csv"])


        # 3. Criticality metric selection
        # suboption = st.radio(":traffic_light: Select criticality metric", ['ttc', 'thw', 'dhw', 'Self-define'])
        # Define your main options
        options_metric = {
            "Acceleration-Scale": ["Deceleration to safety time (DST)", "Required longitudinal acceleration (RLoA)", "Required lateral acceleration (RLaA)", "Required acceleration (RA)"],
            "Distance-Scale": ["Proportion of Stopping Distance (PSD)", "Distance Headway (DHW)"],
            "Jerk-Scale": ["Longitudinal jerk (LongJ)", "Lateral jerk (LatJ)"],
            "Time-Scale": ["Encroachment Time (ET)", "Post-encroachment Time (PET)", "Potential Time To Collision (PTTC)", \
                           "Time Exposed TTC (TET)", \
                            "Time Integrated TTC (TIT)", "Time To Closest Encounter (TTCE)", "Time To Brake (TTB)",\
                                "Time To Kickdown (TTK)", "Time To Steer (TTS)", "Time To Collision (TTC)",\
                                    "Time Headway (THW)"],
            "Velocity-Scale": ["delta_v"]
        }
        # Let the user select a main option
        main_option = st.selectbox("Select a main option:", list(options_metric.keys()))
        # Get the suboptions for the selected main option
        suboptions = options_metric[main_option]
        # Let the user select suboptions. You can use multiselect if multiple selections are needed
        suboption_metric = st.selectbox("Select a suboption:", suboptions)
        # If select "ET", "PET", or "PSD", then conflict area is needed
        conflict_area = None
        if suboption_metric == "Encroachment Time (ET)" or suboption_metric == "Post-encroachment Time (PET)" or suboption_metric == "Proportion of Stopping Distance (PSD)":
            CA_Input = st.text_input("Enter Conflict Area (CA)", [(140, 7), (140, 11), (160, 7), (160, 11)], help="Modify the number properly to get your own CA")
            try:
                conflict_area = ast.literal_eval(CA_Input)
            except ValueError:
                st.warning("Invalid input format. Please enter a list of tuples.")
        # If select "TET" or "TIT"
        target_value = None
        if suboption_metric == "Time Exposed TTC (TET)" or suboption_metric == "Time Integrated TTC (TIT)":
            target_value = st.number_input('Enter a float value', format='%f')
            


        # 4. Set metric threshold to search scenarios in dataset
        # if selected_page == "Criticality":
        range_input = st.text_input("Input the metric threshold range (min - max):")
        if range_input is not None:
            try:
                min_value, max_value = map(float, range_input.split(" - "))
            except ValueError:
                st.warning("Please enter a valid range in the format 'min - max'")
                min_value, max_value = float('nan'), float('nan')

            # Display the selected range
            st.write(f"Minimum Value: {min_value}")
            st.write(f"Maximum Value: {max_value}")
            metric_threshold = (min_value, max_value)


    return dataset_option, main_option, suboption_metric, dataset_load, metric_threshold, conflict_area, target_value




