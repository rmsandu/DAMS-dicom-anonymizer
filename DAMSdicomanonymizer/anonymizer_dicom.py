# -*- coding: utf-8 -*-
"""
Created on June 06th 2019

@author: Raluca Sandu
"""
import os
import pydicom
from pydicom import uid


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
