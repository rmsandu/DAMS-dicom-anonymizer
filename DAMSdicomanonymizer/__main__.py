import argparse
import os
import pandas as pd
import DAMSdicomanonymizer.anonymizer_dicom as anonymizer_dicom

from ast import literal_eval
from DAMSdicomanonymizer.ReferenceTags.create_reference_tags_segmentations import main_add_reference_tags_dcm
from DAMSdicomanonymizer.XML import anonymization_xml_logs
from DAMSdicomanonymizer.XML.define_paths_encoding import create_dict_paths_series_dcm
from DAMSdicomanonymizer.XML.extract_segm_paths_xml import create_dict_paths_series_xml


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--rootdir", required=True, help="input single patient folder path to be processed")
    ap.add_argument("-n", "--patient_name", required=True,
                    help="patient name to be encoded into the files. eg: MAVM03")
    ap.add_argument("-u", "--patient_id", required=True, help="patient id to be encoded into the files. eg: M03")
    ap.add_argument("-d", "--patient_dob", required=True, help="patient date of birth in format eg: 19380101")

    ap.add_argument("-s", "--fix_segmentation_series", required=False, help="fix SeriesInstance UIDs of Segmentations")
    ap.add_argument("-x", "--xml_encoding", required=False, help="encode XML files")
    ap.add_argument("-m", "--mapping_segmentations", required=False,
                    help="create Reference Sequence Tags to refer to segmentations")
    ap.add_argument("-b", "--input_batch_proc", required=False, help="input Excel file for batch processing")
    args = vars(ap.parse_args())
    return args


if __name__ == '__main__':

    args = get_args()
    if args["input_batch_proc"] is not None:
        print("Batch Processing Enabled, path to csv: ", args["input_batch_proc"])
    elif args["input_batch_proc"] is None:
        print("Patient Name:", args["patient_name"])
        print("Patient ID:", args["patient_id"])
        # todo: integrity check for patient-data-of-birth
        print("Patient date-of-birth:", args["patient_dob"])
        print("Rootdir:", args['rootdir'])

    if args["input_batch_proc"] is None:
        # 1. encode or anonymize single patient folder
        anonymizer_dicom.encode_dcm_files_patient(args["rootdir"], args["patient_name"], args["patient_id"],
                                                  args["patient_dob"])
        if args["fix_segmentation_series"] is not None:
            # 2. create dictionary of filepaths and SeriesUIDs
            anonymizer_dicom.fix_segmentations_dcm_tags(args["rootdir"], args["patient_name"], args["patient_id"],
                                                        args["patient_dob"])
            # 3. XML encoding. rewrite the series and the name in the xml after re-writing the broken series uid
            list_all_ct_series = create_dict_paths_series_dcm(args["rootdir"])
            df_ct_mapping = pd.DataFrame(list_all_ct_series)
        if args["xml_encoding"] is not None:
            # 4. create dict of xml and dicom paths
            anonymization_xml_logs.main_encode_xml(args["rootdir"], args["patient_id"], args["patient_name"],
                                                   args["patient_dob"], df_ct_mapping)
            # create dict of xml and dicom paths
            df_segmentations_paths_xml = create_dict_paths_series_xml(args["rootdir"])
        if args["mapping_segmentations"] is not None:
            # 5. Edit each DICOM Segmentation File  by adding reference Source CT and the related segmentation
            if df_segmentations_paths_xml.empty:
                print('No Segmentations Found for Patient:', args["rootdir"])
            else:
                # Edit each DICOM Segmentation File  by adding reference Source CT and the related segmentation
                main_add_reference_tags_dcm(args["rootdir"], df_ct_mapping, df_segmentations_paths_xml)
        print("Patient Folder Anonymized/Encoded:", args["patient_name"])

    else:
        # todo: fix batch processing
        # batch processing and I will assume you have a type of file (excel in this case) with filepaths to multiple folders
        df = pd.read_excel(args["input_batch_proc"])
        df.drop_duplicates(subset=["Patient_ID"], inplace=True)
        df.reset_index(inplace=True)
        df['Patient_Dir_Paths'].fillna("[]", inplace=True)
        df['Patient_Dir_Paths'] = df['Patient_Dir_Paths'].apply(literal_eval)
        # remove the dash from the PatientName variable
        df['Patient Name'] = df['Patient Name'].map(lambda x: x.split('-')[0] + x.split('-')[1])
        for idx in range(len(df)):
            patient_id = str(df["Patient_ID"].iloc[idx])
            patient_dob = str(df['Date_of_Birth'].iloc[idx])
            patient_name = str(df['Patient_Name'].iloc[idx])
            patient_dir_paths = df.Patient_Dir_Paths[idx]
            if len(patient_dir_paths) > 0:
                for rootdir in patient_dir_paths:
                    rootdir = os.path.normpath(rootdir)
                    anonymizer_dicom.encode_dcm_files_patient(rootdir, patient_name, patient_id, patient_dob)
                    # for each patient folder associated with a patient encode the DCM and the XML
                    anonymizer_dicom.fix_segmentations_dcm_tags(rootdir, patient_name, patient_id, patient_dob)
                    # 2. create dictionary of filepaths and SeriesUIDs
                    list_all_ct_series = create_dict_paths_series_dcm(rootdir)
                    df_ct_mapping = pd.DataFrame(list_all_ct_series)
                    # 3. XML encoding. rewrite the series and the name in the xml after re-writing the broken series uid
                    anonymization_xml_logs.main_encode_xml(rootdir, patient_id, patient_name, patient_dob,
                                                           df_ct_mapping)
                    # 4. create dict of xml and dicom paths
                    df_segmentations_paths_xml = create_dict_paths_series_xml(rootdir)
                    # 5. Edit each DICOM Segmentation File  by adding reference Source CT and the related segmentation
                    if df_segmentations_paths_xml.empty:
                        print('No Segmentations Found for Patient:', rootdir)
                        continue
                    else:
                        main_add_reference_tags_dcm(rootdir, df_ct_mapping, df_segmentations_paths_xml)
                        print("Patient Folder Segmentations Fixed:", patient_name)
