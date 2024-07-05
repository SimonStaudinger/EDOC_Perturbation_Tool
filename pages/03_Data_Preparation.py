import uuid
import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu
from functions.functions_Modeling import getDefault
from functions.fuseki_connection import getTimestamp, determinationActivity, \
    getAttributesDataPreparation, getUniqueValuesSeq, \
    getDataRestrictionSeq, get_dataset, getRestriction, invalidateWasGeneratedBy, retrieveFeatureUUID, \
    uplaod_missing_value_to_feature, uplaod_bin_value_to_feature, uplaodSequence

host, host_upload = get_dataset()

try:
    getUniqueValuesSeq(host)

except Exception as e:
    st.error("Please upload feature values in Data Understanding step")
    if st.button("Data Understanding"):
        switch_page("Data Understanding")
    st.stop()
try:
    getDefault(host)
except:
    st.error("Please select other dataset or refresh page")
    st.stop()


if "data_restriction_final" not in st.session_state:
    st.session_state.data_restriction_final = st.session_state.unique_values_dict

if st.session_state.dataframe_feature_names.empty:
    st.stop()

data_preparation_options = option_menu("Data Preparation Options", ["Binned Features", "Missing Values"],
                                       icons=['collection', 'slash-circle'],
                                       menu_icon="None", default_index=0, orientation="horizontal")
with st.expander("Show Information"):
    try:
        getAttributesDataPreparation(host)
    except:
        st.error("Please select other dataset or refresh page")
        st.stop()
    try:

        uploaded_DataRestriction = getRestriction(host)
        st.session_state["data_restrictions_dict"] = getDataRestrictionSeq(
            uploaded_DataRestriction["DUA.value"][0], host)
        st.session_state.data_restriction_final = st.session_state.unique_values_dict.copy()
        st.session_state.data_restriction_final.update(st.session_state["data_restrictions_dict"])

    except:
        st.warning("No Data Restrictions determined")



if data_preparation_options == "Binned Features":

    if "http://www.dke.uni-linz.ac.at/rprov#Cardinal" not in set(st.session_state.DF_feature_scale_name["scale.value"].to_list()):
        st.info("No Cardinal values determined in this dataset, therefore no binning can be performed")

    colored_header(
        label="Binning of cardinal features",
        description="If feature was binned, insert how it was done.",
        color_name="red-70",
    )


    if "bin_dict" not in st.session_state:
        st.session_state.bin_dict = dict()
    if st.session_state["loaded_bin_dict"] == {}:
        st.write("Please insert upper and lower bound and define amount of bins.")
        for key, values in st.session_state.level_of_measurement_dic.items():
            if values == 'Cardinal':
                if f"bin_{key}" not in st.session_state:
                    st.session_state[f"bin_{key}"] = list()
                with st.expander(f"Bin {key}"):


                    try:
                        lower_border = st.number_input("Select lower border",value =float(st.session_state.data_restriction_final[key][0]), min_value=float(st.session_state.data_restriction_final[key][0]), max_value=float(st.session_state.data_restriction_final[key][-1]), key = f"lower_border_{key}")
                        upper_border = st.number_input("Select upper border",value =float(st.session_state.data_restriction_final[key][-1]),  max_value = float(st.session_state.data_restriction_final[key][-1]),key = f"upper_border_{key}")

                        if st.session_state[f"lower_border_{key}"] >= st.session_state[f"upper_border_{key}"]:
                            st.error("Lower bound range must be smaller than upper bound.")
                        else:
                            bins = st.number_input("Select amount of bins", min_value=int(1), key=f"amount_bin_{key}", help="Amount of bins has to be higher one in order to create bins")
                            step = (upper_border - lower_border) / (bins)


                            if bins > 1:
                                st.session_state[f"bin_{key}"] = [
                                    round(lower_border + n * step, 1) for n in
                                    range(bins + 1)]
                                st.session_state["bin_dict"][key] = st.session_state[f"bin_{key}"]
                                st.success(f"Bin for {key} saved, please upload when finished.")

                            else:
                                try:
                                    del st.session_state["bin_dict"][key]
                                except:
                                    pass
                    except:
                        st.error("Lower bound range must be smaller than upper bound.")

        if st.session_state.bin_dict != {}:
            st.write("------------------")
            with st.expander("Show bins"):
                st.write(st.session_state.bin_dict)
            if st.button("Upload bins", key="button_bins", type="primary"):
                determinationName = 'DocuOfRangeOfBinnedFeature'
                label = "DocuOfRangeOfBinnedFeature"

                name = 'RangeOfBinnedFeature'
                rprovName = 'RangeOfBinnedFeature'


                uuid_determinationBin = determinationActivity(host_upload, determinationName, label)

                with st.spinner("Uploading..."):
                    for key, value in st.session_state["bin_dict"].items():

                        featureUUID = retrieveFeatureUUID(host, key)

                        # Upload the sequence with the values first.
                        seqUUID = uuid.uuid4()
                        i = 0
                        for values in value:
                            uplaodSequence(host_upload, seqUUID, i, values)
                            i = i + 1

                        uplaod_bin_value_to_feature(host_upload, seqUUID, f"{rprovName} {key}", featureUUID, uuid_determinationBin)
                        st.success("Upload successful")

                st.experimental_rerun()
    else:
        st.markdown("""
                       **Here you can see how bins were generated for each feature**

                       If you want to change click on the button below.
                       """)
        st.write(st.session_state["loaded_bin_dict"])

        if st.button("Delete bins"):
            #deleteWasGeneratedByDPA(host_upload, st.session_state["DF_bin_dict"])
            invalidateWasGeneratedBy(host_upload,st.session_state["DF_bin_dict"]["DPA.value"][0],'DPA')
            del st.session_state["loaded_bin_dict"]
            del st.session_state["DF_bin_dict"]

            st.experimental_rerun()

elif data_preparation_options == "Missing Values":

    determinationNameUUID = 'DocuOfHandlingOfMissingValues'
    determinationName = 'DocuOfHandlingOfMissingValues'
    label = 'Documentation of missing values for the features.'

    ending_time = getTimestamp()

    colored_header(
        label="Missing values of features",
        description="If missing values of feature were replaced, insert how it was done.",
        color_name="red-70",
    )

    tab1, tab2, tab3 = st.tabs(["Cardinal", "Ordinal", "Nominal"])

    if st.session_state.loaded_missingValues_of_features_dic=={}:

    # create a dictionary with features which have missing values
        for key, values in st.session_state.level_of_measurement_dic.items():
            if 'missingValues_of_features_dic' not in st.session_state:
                st.session_state["missingValues_of_features_dic"] = dict()

            if key in st.session_state["missingValues_of_features_dic"]:
                st.session_state[f'missingValues_{key}'] = \
                    st.session_state["missingValues_of_features_dic"][key]
            else:
                st.session_state[f'missingValues_{key}'] = ""

            if values == 'Cardinal':
                with tab1:
                    with st.expander(f"Missing Values of {key}"):

                        st.session_state[f'missingValues_{key}'] = st.text_input("How were missing values replaced?", value=st.session_state[f'missingValues_{key}'],key=(f'missingValues_{key}_widget'))
                        if st.session_state[f'missingValues_{key}'] != "":
                            st.session_state["missingValues_of_features_dic"][key]=st.session_state[f'missingValues_{key}']
            elif values == 'Ordinal':
                with tab2:
                    with st.expander(f"Missing Values of {key}"):
                        st.session_state[f'missingValues_{key}'] = st.text_input("How were missing values replaced?", value=st.session_state[f'missingValues_{key}'],key=(f'missingValues_{key}_widget'))
                        if st.session_state[f'missingValues_{key}'] != "":
                            st.session_state["missingValues_of_features_dic"][key]=st.session_state[f'missingValues_{key}']
            elif values == 'Nominal':
                with tab3:
                    with st.expander(f"Missing Values of {key}"):
                        st.session_state[f'missingValues_{key}'] = st.text_input("How were missing values replaced?", value=st.session_state[f'missingValues_{key}'],key=(f'missingValues_{key}_widget'))
                        if st.session_state[f'missingValues_{key}'] != "":
                            st.session_state["missingValues_of_features_dic"][key]=st.session_state[f'missingValues_{key}']
        if st.session_state["missingValues_of_features_dic"]!= {}:
            st.write("------------------")
            with st.expander("Show missing values"):
                st.write(st.session_state["missingValues_of_features_dic"])
            if st.button("Submit", type="primary"):
                uuid_DocuOfHandlingOfMissingValues = determinationActivity(host_upload, determinationName, label)

                name = "HandlingOfMissingValues"

                #uploadMissingValues(host_upload, host, st.session_state["missingValues_of_features_dic"], uuid_DocuOfHandlingOfMissingValues, name)
                with st.spinner("Uploading..."):
                    for key, value in st.session_state["missingValues_of_features_dic"].items():

                        featureUUID = retrieveFeatureUUID(host, key)

                        uplaod_missing_value_to_feature(host_upload, key, value, featureUUID, uuid_DocuOfHandlingOfMissingValues)

                st.session_state.loaded_missingValues_of_features_dic = st.session_state["missingValues_of_features_dic"]
                st.experimental_rerun()
    else:
        st.markdown("""
                **Here you can see how missing values were replaced for each feature**

                If you want to change click on the button below.
                """)
        st.write(st.session_state["loaded_missingValues_of_features_dic"])

        if st.button("Invalidate missing values"):
            invalidateWasGeneratedBy(host_upload, st.session_state["DF_feature_missing_values_dic"]["DPA.value"][0], 'DPA')
            del st.session_state["loaded_missingValues_of_features_dic"]
            del st.session_state["DF_feature_missing_values_dic"]

            st.experimental_rerun()
