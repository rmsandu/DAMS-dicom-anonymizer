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

**Now, the cool fun stuff (in my personal subjective opinion)**.
As far as I am aware at this point when I am writing the ReadMe, the way that the segmentations and source images are "connected" for training, segmentation, evaluation purposes (etc, you name it), it's by either having them in the same folder, or in some other folders plus having a CSV/Text/Excel file more often that in tabular format which stores the paths to the (source) image and the other images related to it.

I wanted to avoid this file system path generation, because I either forget where I place my files, or I move them around a lot, or my admin changes the name of my database folder (jk). That being said, I discovered this 2 cool metatags which are actually **Metatags Sequences**, i.e., they hold several metatags under them , in a parent-child type of relationship. It's important to note that these tags are actually **Sequences** because they are edited and read in a different manner than simple non-hierachical tags.


The tags that I used are:
- [**ReferencedImageSequenceTag**](https://dicom.innolitics.com/ciods/basic-structured-display/structured-display-image-box/00720422/00081140) 
- [**SourceImageSequence**](https://dicom.innolitics.com/ciods/rt-beams-treatment-record/general-reference/00082112).

I used the `ReferencedImageSequence` to store the relation between the tumor and ablation segmentation. Thus, the tumor segmentation will store the `SeriesInstanceUID`, `SOPClassUID` and lesion number `ReferencedSegmentNumber` of the ablation segmentation and vice-versa. The `SourceImageSequence` contains the `SeriesInstanceUID` of the original initial CT source image from which the segmentation mask was derived. 

The library:  
    `from pydicom import uid`  
    `from pydicom.dataset import Dataset`  
    `from pydicom.sequence import Sequence`  
The code:  

     def add_general_reference_segmentation(dataset_segm,
                                       ReferencedSeriesInstanceUID_segm,
                                       ReferencedSOPInstanceUID_src,
                                       StudyInstanceUID_src,
                                       segment_label,
                                       lesion_number
                                       ):  
                                       
    """
    `Add Reference to the tumour/ablation and source img in the DICOM segmentation metatags.` 
    `:param dataset_segm: dcm file read with pydicom library`
    `:param ReferencedSOPInstanceUID_segm: SeriesInstanceUID of the related segmentation file (tumour or ablation)`
    `:param ReferencedSOPInstanceUID_src: SeriesInstanceUID of the source image`
    `:param StudyInstanceUID_src: StudyInstanceUID of the source image`
    `:param segment_label: text describing whether is tumor or ablation`
    `:param: lesion_number: a int identifying which lesion was this`
    `:return: dicom single file/slice with new General Reference Sequence Tags`
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

## External Libraries
- `PyDicom` (for DICOM processing)
- `Untagle` (for XML files processing)
## Usage
 The script that is called first is `A_fix_segmentations_dcm.py` (very creative I know, couldn't come up with a better name for the moment). The `__main__` has single and batch (multiple patient folders) options.
After running the scripts a message is generated that the metatags have been modified.  

 You can see how I actually use the tags later to find the corresponding source-segmentations images in the [segmnetation-eval](https://github.com/raluca-san/segmentation-eval) repository.
### Single Patient Folder
I work with `ArgumentParser`. For a single patient encoding call the script like for example:  
     `A_fix_segmentations_dcm.py --i "C:\patientfolder\PAT_M001" --patient_name "MEVR001" --patient_ID "R001" --patient_dob "19500101" --a True`  

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
## DISCLAIMER
Not 100% sure that this complies to the DICOM standard, but I don't see why it would not. If you do not want to modify your raw data (which I never recommend to), make a copy, and then run this script that modifies the tags.


## Extra info (for those lazy to click the links of the definition)
Here's a screenshot of both of their definitions:
![image](https://user-images.githubusercontent.com/20581812/77447245-c2246d80-6def-11ea-81b6-cd2dd35fd6c2.png)
![image](https://user-images.githubusercontent.com/20581812/77447687-3c54f200-6df0-11ea-9813-036192801b96.png)

#TODO: add more info on how the mapping is retrieved using dictionary keys and values.
