# -*- coding: utf-8 -*-
"""
Created on June 06th 2019

@author: Raluca Sandu
"""

import argparse
import os
from ast import literal_eval

import pandas as pd
import pydicom
from pydicom import uid


from DAMSdicomanonymizer.XML import anonymization_xml_logs
from DAMSdicomanonymizer.ReferenceTags.create_reference_tags_segmentations import main_add_reference_tags_dcm
from DAMSdicomanonymizer.XML.define_paths_encoding import create_dict_paths_series_dcm
from DAMSdicomanonymizer.XML.extract_segm_paths_xml import create_dict_paths_series_xml


def encode_dcm_files_patient(rootdir, patient_name, patient_id, patient_dob):
    """
    :param rootdir:
    :param patient_name:
    :param patient_id:
    :param patient_dob:
    :return:
    """
    for subdir, dirs, files in os.walk(rootdir):
        for file in sorted(files):  # sort files by date of creation
            DcmFilePathName = os.path.join(subdir, file)
            try:
                dcm_file = os.path.normpath(DcmFilePathName)
                dataset = pydicom.read_file(dcm_file)
            except Exception as e:
                # print(repr(e))
                continue  # not a DICOM file
            dataset.PatientName = patient_name
            dataset.PatientID = patient_id
            dataset.PatientBirthDate = patient_dob
            dataset.PatientSex = "None"
            dataset.InstitutionName = "None"
            dataset.InstitutionAddress = "None"
            dataset.InstitutionalDepartmentName = "None"
            dataset.StudyName = "None"
            dataset.OperatorsName = "None"
            dataset.DeviceSerialNumber = "None"
            dataset.ReferringPhysicianName = "None"
            dataset.AcquisitionTime = "None"
            dataset.StudyTime = "None"
            dataset.ContentDate = "None"
            dataset.AcquisitionDateTime = "None"
            dataset.ContentTime = "None"
            dataset.save_as(dcm_file)


def fix_segmentations_dcm_tags(rootdir, patient_name, patient_id, patient_dob):
    """

    :param rootdir:
    :param patient_name:
    :param patient_id:
    :param patient_dob:
    :return:
    """
    series_no = 50  # take a random series number for the segmentations
    for subdir, dirs, files in os.walk(rootdir):
        if ('Segmentations' in subdir) and ('SeriesNo_' in subdir):
            k = 1
            series_no += 1
            SeriesInstanceUID_segmentation = uid.generate_uid()  # generate a new series instance uid for each folder
            for file in sorted(files):
                DcmFilePathName = os.path.join(subdir, file)
                try:
                    dcm_file = os.path.normpath(DcmFilePathName)
                    dataset_segm = pydicom.read_file(dcm_file)
                except Exception as e:
                    print(repr(e))
                    continue  # not a DICOM file
                # next lines will be executed only if the file is DICOM
                dataset_segm.PatientName = patient_name
                dataset_segm.PatientID = patient_id
                dataset_segm.PatientBirthDate = patient_dob
                dataset_segm.InstitutionName = "None"
                dataset_segm.InstitutionAddress = "None"
                dataset_segm.SliceLocation = dataset_segm.ImagePositionPatient[2]
                dataset_segm.SOPInstanceUID = uid.generate_uid()
                dataset_segm.SeriesInstanceUID = SeriesInstanceUID_segmentation
                dataset_segm.InstanceNumber = k
                dataset_segm.SeriesNumber = series_no
                k += 1  # increase the instance number
                dataset_segm.save_as(dcm_file)  # save to disk


if __name__ == '__main__':

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
        encode_dcm_files_patient(args["rootdir"], args["patient_name"], args["patient_id"], args["patient_dob"])
        if args["fix_segmentation_series"] is not None:
            # 2. create dictionary of filepaths and SeriesUIDs
            fix_segmentations_dcm_tags(args["rootdir"], args["patient_name"], args["patient_id"], args["patient_dob"])
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
                    encode_dcm_files_patient(rootdir, patient_name, patient_id, patient_dob)
                    # for each patient folder associated with a patient encode the DCM and the XML
                    fix_segmentations_dcm_tags(rootdir, patient_name, patient_id, patient_dob)
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
