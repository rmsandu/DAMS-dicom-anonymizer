# -*- coding: utf-8 -*-
"""
@author: Raluca Sandu
"""
import os
import sys

import pydicom
from pydicom.dataset import Dataset
from pydicom.sequence import Sequence


def generate_reference_segmentation_tags(dataset_segm,
                                         ReferencedSeriesInstanceUID_segm,
                                         ReferencedSOPInstanceUID_src,
                                         StudyInstanceUID_src,
                                         segment_label,
                                         lesion_number
                                         ):
    """
    Add Reference to the tumour/ablation and source img in the DICOM segmentation metatags.
    :param dataset_segm: dcm file read with pydicom library
    :param ReferencedSOPInstanceUID_segm: SeriesInstanceUID of the related segmentation file (tumour or ablation)
    :param ReferencedSOPInstanceUID_src: SeriesInstanceUID of the source image
    :param StudyInstanceUID_src: StudyInstanceUID of the source image
    :param segment_label: text describing whether is tumor or ablation
    :param: lesion_number: a int identifying which lesion was this
    :return: dicom single file/slice with new General Reference Sequence Tags
    """

    if segment_label == "Lession":
        dataset_segm.SegmentLabel = "Tumor"
    elif segment_label == "AblationZone":
        dataset_segm.SegmentLabel = "Ablation"

    dataset_segm.StudyInstanceUID = StudyInstanceUID_src
    dataset_segm.SegmentationType = "BINARY"
    dataset_segm.SegmentAlgorithmType = "SEMIAUTOMATIC"
    dataset_segm.DerivationDescription = "CasOneIR"
    dataset_segm.ImageType = "DERIVED\PRIMARY"

    Segm_ds = Dataset()
    Segm_ds.ReferencedSOPInstanceUID = ReferencedSeriesInstanceUID_segm
    Segm_ds.ReferencedSOPClassUID = dataset_segm.SOPClassUID
    Segm_ds.ReferencedSegmentNumber = lesion_number

    Source_ds = Dataset()
    Source_ds.ReferencedSOPInstanceUID = ReferencedSOPInstanceUID_src

    dataset_segm.ReferencedImageSequence = Sequence([Segm_ds])
    dataset_segm.SourceImageSequence = Sequence([Source_ds])

    return dataset_segm


def main_add_reference_tags_dcm(rootdir, df_ct_mapping, df_segmentations_paths_xml):
    """

    :param rootdir:
    :param df_segmentations_paths_xml:
    :param df_ct_mapping:
    :return:
    """
    for subdir, dirs, files in os.walk(rootdir):
        k = 1
        if 'Segmentations' in subdir and 'SeriesNo_' in subdir:
            for file in sorted(files):
                DcmFilePathName = os.path.join(subdir, file)
                try:
                    dcm_file = os.path.normpath(DcmFilePathName)
                    dataset_segm = pydicom.read_file(dcm_file)
                except Exception as e:
                    print(repr(e))
                    continue  # not a DICOM file
                path_segmentations_idx = subdir.find("Segmentations")
                path_segmentations_folder = subdir[path_segmentations_idx - 1:]
                try:
                    idx_segm_xml = df_segmentations_paths_xml.index[
                        df_segmentations_paths_xml["PathSeries"] == path_segmentations_folder].tolist()[0]
                except Exception as e:
                    continue
                    # print(repr(e), "whats happening here")
                # get the timestamp value at the index of the identified segmentation series_uid both the Plan.xml (
                # tumour path) and Ablation_Validation.xml (ablation) have the same starting time in the XML
                # find the other segmentation with the matching start time != from the seriesinstanceuid read atm
                segm_instance_uid_val = df_segmentations_paths_xml.SegmentationSeriesUID_xml[idx_segm_xml]
                needle_idx_val = df_segmentations_paths_xml.NeedleIdx[idx_segm_xml]
                time_start_segm_val = df_segmentations_paths_xml.TimeStartSegmentation[idx_segm_xml]
                ReferencedSOPInstanceUID_src = \
                    df_segmentations_paths_xml.loc[idx_segm_xml].SourceSeriesID
                # get the SeriesInstanceUID of the source CT from the XML files.
                # 1) look for it in DF of the source CTs
                # 2) get the corresponding StudyInstanceUID
                try:
                    idx_series_source_study_instance_uid = df_ct_mapping.index[
                        df_ct_mapping['SeriesInstanceNumberUID'] == ReferencedSOPInstanceUID_src].tolist()

                    if not idx_series_source_study_instance_uid:
                        series_number = df_segmentations_paths_xml.loc[idx_segm_xml].SeriesNumber
                        idx_series_source_study_instance_uid = df_ct_mapping.index[
                            df_ct_mapping['SeriesNumber'] == int(series_number)].tolist()
                    if len(idx_series_source_study_instance_uid) > 1:
                        continue
                        # print('The StudyInstanceUID for the segmentations is not unique at the following address: ',
                        #       DcmFilePathName)
                        # sys.exit()
                    StudyInstanceUID_src = df_ct_mapping.loc[idx_series_source_study_instance_uid[0]].StudyInstanceUID

                except Exception as e:
                    continue
                    # print(repr(e))
                needle_idx_df_xml = df_segmentations_paths_xml.index[
                    df_segmentations_paths_xml["NeedleIdx"] == needle_idx_val].tolist()
                idx_referenced_segm = [el for el in needle_idx_df_xml if el != idx_segm_xml]
                if len(idx_referenced_segm) > 1:
                    # print('The SeriesInstanceUID for the segmentations is not unique at the following address: ',
                    #       DcmFilePathName)
                    # do the matching based on the time of the segmentations
                    time_start_idx_df_xml = df_segmentations_paths_xml.index[
                        df_segmentations_paths_xml["TimeStartSegmentation"] == time_start_segm_val].tolist()
                    idx_referenced_segm = [el for el in time_start_idx_df_xml if el != idx_segm_xml]

                # %% get the path series instead of the segmentationseriesuid_xml
                #  read the SeriesInstanceUID from the DICOM file (take the path)
                if idx_referenced_segm:
                    ReferencedSOPInstanceUID_path = \
                        df_segmentations_paths_xml.loc[idx_referenced_segm[0]].PathSeries
                elif len(idx_referenced_segm) > 1:
                    print('Multiple Segmentation Folders present.,'
                          'Please clean ')
                    sys.exit()
                else:
                    ReferencedSOPInstanceUID_path = None
                if ReferencedSOPInstanceUID_path is None:
                    segment_label = 0
                    lesion_number = 0
                    ReferencedSOPInstanceUID_ds = "None"
                    ReferencedSeriesInstanceUID_segm = "None"
                else:
                    referenced_dcm_dir = subdir[
                                         0:len(subdir) - len(path_segmentations_folder)] + ReferencedSOPInstanceUID_path
                    try:
                        segm_file = os.listdir(referenced_dcm_dir)[0]
                    except FileNotFoundError:
                        # print('No Files have been found at the specified address: ', referenced_dcm_dir)
                        continue  # go back to the beginning of the loop
                    ReferencedSOPInstanceUID_ds = pydicom.read_file(os.path.join(referenced_dcm_dir, segm_file))
                    ReferencedSeriesInstanceUID_segm = ReferencedSOPInstanceUID_ds.SeriesInstanceUID
                    segment_label = df_segmentations_paths_xml.loc[idx_segm_xml].SegmentLabel
                    lesion_number = df_segmentations_paths_xml.loc[idx_segm_xml].NeedleIdx + 1
                # call function to change the segmentation uid
                dataset_segm = generate_reference_segmentation_tags(dataset_segm,
                                                                    ReferencedSeriesInstanceUID_segm,
                                                                    ReferencedSOPInstanceUID_src,
                                                                    StudyInstanceUID_src,
                                                                    segment_label,
                                                                    lesion_number)
                dataset_segm.save_as(dcm_file)  # save to disk
