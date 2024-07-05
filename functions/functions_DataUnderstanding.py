import streamlit as st
def update_data_restrictions_cardinal(key):
    st.session_state['data_restrictions_dict'][key] = st.session_state[f'data_restrictions_{key}']

def update_data_restrictions_ordinal(key):
    st.session_state[f'data_restrictions_{key}_ordinal'] = st.session_state[f'data_restrictions_{key}']
    st.session_state['data_restrictions_dict'][key] = st.session_state[f'data_restrictions_{key}']

def update_data_restrictions_nominal(key):
    st.session_state[f'data_restrictions_{key}_nominal'] = st.session_state[f'data_restrictions_{key}']
    st.session_state['data_restrictions_dict'][key] = st.session_state[f'data_restrictions_{key}']

def update_feature_sensor_precision(key):
    st.session_state[f'feature_sensor_precision_{key}'] = st.session_state[f'feature_sensor_precision_{key}_widget']
    if st.session_state[f'feature_sensor_precision_{key}'] == 0:
        del st.session_state['feature_sensor_precision_dict'][key]
    else:
        st.session_state['feature_sensor_precision_dict'][key] = st.session_state[f'feature_sensor_precision_{key}']

#This method saves the maximum allowed values as data restriction and removes possible narrower ones
# @param key the name of the feature
def defaultValuesCardinal(key):
    #Use the maximum allowed values as data restriction
    try:
        st.session_state[f'data_restrictions_{key}_cardinal'] = [float(st.session_state.unique_values_dict[key][0]),float(st.session_state.unique_values_dict[key][-1])]
    except:
        st.info("Feature is not Cardinal")
    try:
        #Delete a custom data restriction that
        del st.session_state["data_restrictions_dict"][key]
    except:
        st.info("Default values already selected")

def defaultValuesOrdinal(key):
    st.session_state[f'data_restrictions_{key}_ordinal'] = st.session_state.unique_values_dict[key]
    try:
        del st.session_state["data_restrictions_dict"][key]
    except:
        st.info("Default values already selected")

def defaultValuesNominal(key):
    st.session_state[f'data_restrictions_{key}_nominal'] = st.session_state.unique_values_dict[key]
    try:
        del st.session_state["data_restrictions_dict"][key]
    except:
        st.info("Default values already selected")
