# DAMS
DAMS aka DICOM-Anomymization-Mapping-Script

## Description
These scripts perform some simple DICOM encoding (anonymization) and mapping between the source CT images and the segmentation masks that were derived from them. My data also contains XML files with patient related info in them so I anonymized those as well (see `anonymization_xml_logs.py`). My anonymization is not anonymization per-se, but **encoding** of the patient specific details with a mapping key. Since I later need to relate the image information (radiomics) with clinical data I need a specific key for each patient. Of course, you can generate random keys, if you do not need to know the patient mapping. Moreover, you can also edit (anonymize) more fields.  

The following DICOM metatags are encoded/anonymized:
- `PatientName (0010,0010)`
- `PatientID 	(0010,0020)`
- `PatientBirthDate 	(0010,0030)` (I kept the year of birth, set the month and day to 0101)
- `InstitutionName`
- `InstitutionAddress`
- `StudyName`


## External Libraries
- `PyDicom` (for DICOM processing)
- `Untagle` (for XML files processing)
## Usage for Single Patient Folder
 The script that is called first is 
 
     `DAMS-dicom-anonymizer --i "C:\patientfolder\PAT_M001" --patient_name "MEVR001" --patient_ID "R001" --patient_dob "19500101"
     
The following functions are then called:
- ` anonymize_all_dcm_files(rootdir, patient_name, patient_id, patient_dob)`
- ` encode_segmentations_dcm_tags(rootdir, patient_name, patient_id, patient_dob)`
- ` anonymization_xml_logs.main_encode_xml(rootdir, patient_id, patient_name, patient_dob, df_ct_mapping)`
- ` main_add_reference_tags_dcm(rootdir, df_ct_mapping, df_segmentations_paths_xml)`

### Batch Processing (multiple patients)
`A_fix_segmentations_dcm.py --input_batch_proc "C:\patientfolder\all_my_patients_filepaths_in_here.xlsx" --a "True`.
This option reads an Excel file using `Pandas` and goes row by row in the field *Patient_ID* and *Patient_Dir_Paths*. That's the only difference from the single patient folder processing.
## Output
Anonymized DICOM files re-written to disk. Careful, this script overwrites the original data. If you want to save it somewhere else, modify the scipt. `PyDicom` has the "save_as(filepath)" option for each individual DICOM slice (which I also used).



