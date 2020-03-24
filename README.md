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

## Segmentation-Source Key Mapping

First of all, I had to perform some metatag corrections on my segmentations since some tags were incorrect. The tags were corrupted by the segmentation tool I have used to create the masks (not open source, not commercial, long story). Therefore, first  I had to generate a new `SeriesInstanceUID` and `SOPInstanceUID ` using `pydicom.uid.generate_uid()`. Then, I corrected the `InstanceNumber` for each slice, since in my original segmentations it was the same number for all slices. Last, I created some random dumb `SeriesNumber`, which was different than the SeriesNumber from the Source CTs. I needed the SeriesNumber to be able to load in my Annotation Software and database (I worked with Brainlab's Quentry database storage solution).

The code for these is in the `def encode_segmentations_dcm_tags(rootdir, patient_name, patient_id, patient_dob)`. Most probably you won't need to run this function.

Now, the cool fun stuff (in my personal subjective opinion).

It does that by creating a dictionary of paths based on the metadata information that was encoded in the [**ReferencedImageSequenceTag**](https://dicom.innolitics.com/ciods/basic-structured-display/structured-display-image-box/00720422/00081140) and [**SourceImageSequence**](https://dicom.innolitics.com/ciods/rt-beams-treatment-record/general-reference/00082112).


## External Libraries
- `PyDicom` (for DICOM processing)
- `Untagle` (for XML files processing)
## Usage
 blabla to do
### Single Patient Folder

### Batch Processing (multiple patients)

## Output
Anonymized DICOM files re-written to disk. Careful, this script overwrites the original data. If you want to save it somewhere else, modify the scipt.
