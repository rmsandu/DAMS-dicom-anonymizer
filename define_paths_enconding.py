# -*- coding: utf-8 -*-
"""
@author: Raluca Sandu
"""

import os
import pydicom


def create_dict_paths_series_dcm(rootdir):
    list_all_ct_series = []
    for subdir, dirs, files in os.walk(rootdir):
        # study_0, study_1 case?
        path, foldername = os.path.split(subdir)
        if ("Series" in foldername) or ("SegmentationNo" in foldername):
            # get the source image sequence attribute - SOPClassUID
            for file in sorted(files):
                try:
                    dcm_file = os.path.join(subdir, file)
                    dataset_source_ct = pydicom.read_file(dcm_file)
                except Exception:
                    # not dicom file so continue until you find one
                    continue
                source_series_instance_uid = dataset_source_ct.SeriesInstanceUID
                try:
                    source_study_instance_uid = dataset_source_ct.StudyInstanceUID
                except Exception:
                    source_study_instance_uid = None
                source_series_number = dataset_source_ct.SeriesNumber
                source_SOP_class_uid = dataset_source_ct.SOPClassUID
                # if the ct series is not found in the dictionary, add it
                result = next((item for item in list_all_ct_series if
                               item["SeriesInstanceNumberUID"] == source_series_instance_uid), None)
                path_segmentations_idx = subdir.find("Segmentations")
                if path_segmentations_idx != -1:
                    path_segmentations_folder = subdir[path_segmentations_idx - 1:]
                else:
                    path_segmentations_folder = subdir
                if result is None:
                    dict_series_folder = {"SeriesNumber": source_series_number,
                                          "SeriesInstanceNumberUID": source_series_instance_uid,
                                          "SOPClassUID": source_SOP_class_uid,
                                          "StudyInstanceUID": source_study_instance_uid,
                                          "PathSeries": path_segmentations_folder
                                          }
                    list_all_ct_series.append(dict_series_folder)
    return list_all_ct_series

