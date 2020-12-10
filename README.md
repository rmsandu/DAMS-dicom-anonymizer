# DAMS
DAMS aka DICOM-Anomymization-Mapping-Script

## Description
These scripts perform some simple DICOM encoding (anonymization) and mapping between the source CT images and the segmentation masks that were derived from them (optional) by reading the DICOM files one by one using the [PyDicom](https://pydicom.github.io/pydicom/stable/auto_examples/metadata_processing/plot_anonymize.html) library and saving them to disk.

 My data also contains XML files with patient related info in them so I anonymized those as well (see `DAMSanonymizer/XML/anonymization_xml_logs.py`). My anonymization is not anonymization per-se, but **encoding** of the patient specific details with a mapping key. Since I later need to relate the image information (radiomics) with clinical data I need a specific key for each patient. Of course, you can generate random keys or leave the tags empty (None), if you do not need to know the patient mapping. Moreover, you can also edit (anonymize) more fields.  

The following DICOM metatags are encoded/anonymized:
- `PatientName (0010,0010)` - **Encoded**
- `PatientID 	(0010,0020)` - **Encoded**
- `PatientBirthDate 	(0010,0030)` - **Encoded** 

The following DICOM fields were **deleted** (i.e. replaced with `None` value).
- `PatientSex` 
- `InstitutionName`
- `InstitutionAddress`
- `InstitutionalDepartmentName`
- `StudyName`
- `OperatorsName`
- `ReferringPhysicianName`
- `DeviceSerialNumber`
- `AcquisitionTime`
- `AcquisitionDateTime `
- `StudyTime`
- `ContentTime`
- `ContentDate`

## External Libraries
- `PyDicom` (for DICOM processing)
- `Untagle` (for XML files processing)
## Usage for Single Patient Folder 
 To avoid errors keep all the files associated with 1 patient and 1 study (multiple series possible) in one folder, otherwise the de-identification will be inconsistent. The original files will be modified and also will remain grouped in their original patients, studies, and series. Careful about overwriting original raw data.
 To execute the de-identification run the `__main__.py` script. 
     `python -m DAMS-dicom-anonymizer --i "C:\patientfolder\PAT_M001" --patient_name "MEVR001" --patient_id "R001" --patient_dob "19500101"`
    or use the short names:
    `python -m DAMS-dicom-anonymizer -i "C:\Patients\Pat_M07" -n "MAVM07" -u "M07" -d "194901001"`
   
The following functions are then called:
- `get_args()`
- `anonymizer_dicom.encode_dcm_files_patient(args["rootdir"], args["patient_name"], args["patient_id"], args["patient_dob"])`

### Batch Processing (multiple patients)
This option reads an Excel file using `Pandas` and goes row by row in the field *Patient_ID* and *Patient_Dir_Paths*. That's the only difference from the single patient folder processing.
## Output
Anonymized DICOM files re-written to disk. Careful, this script overwrites the original data. If you want to save it somewhere else, modify the scipt. `PyDicom` has the `save_as(filepath)` option for each individual DICOM slice (which I also used).



