from django.db import models
from django.contrib.gis.db import models as gid_models
# from django.contrib.postgres.fields import ArrayField

from utils.common import get_queryset_for_model, validate_xlsform_name
from apps.common.models import UserResource
from apps.project.models import Project


class Questionnaire(UserResource):
    class MetadataCollection(models.IntegerChoices):
        START = 1, 'Start date and time of the survey.'
        END = 2, 'End date and time of the survey.'
        TODAY = 3, 'Day of the survey.'
        DEVICEID = 4, 'Unique client identifier. Can be user-reset.'
        PHONENUMBER = 5, 'Phone number (if available).'
        USERNAME = 6, 'Username configured (if available).'
        EMAIL = 7, 'Email address configured (if available).'
        AUDIT = 8, 'Log enumerator behavior during data entry'

    title = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    # Metadata
    # https://xlsform.org/en/#metadata
    # include_metadata = ArrayField(
    #     models.PositiveSmallIntegerField(choices=MetadataCollection.choices),
    #     default=list,
    #     blank=True,
    # )
    # -- Audit specific data
    # location-priority=high-accuracy location-min-interval=180 location-max-age=300
    # https://docs.getodk.org/form-audit-log/
    # metadata_audit_paramaters = models.CharField(max_length=255)

    # Settings https://xlsform.org/en/#settings-worksheet
    # - allow_choice_duplicates
    # - form_title: The title of the form that is shown to users.
    #     The form title is pulled from form_id if form_title is blank or missing.
    # - form_id: The name used to uniquely identify the form on the server.
    #     The form id is pulled from the XLS file name if form_id is blank or missing.
    # - version: String that represents this version.
    #     A common convention is to use strings of the form 'yyyymmddrr'.
    #     For example, 2017021501 is the 1st revision from Feb 15th, 2017.
    # - instance_name: Expression using form fields to identify for each form submission. Learn more.
    # - default_language: In localized forms, this sets which language should be used as the default.
    #     The same format as described for adding translations should be used, including the language code.
    # - public_key: For encryption-enabled forms, this is where the public key is copied and pasted. Learn more.
    # - submission_url: This url can be used to override the default server where finalized records are
    #   submitted to. Learn more.
    # - style: For web forms, specify the form style. Learn more.
    # - name: XForms root node name. This is rarely needed, learn more.
    project_id: int

    def __str__(self):
        return self.title

    @classmethod
    def get_for(cls, user, queryset=None):
        project_qs = Project.get_for(user)
        return get_queryset_for_model(cls, queryset=queryset).filter(project__in=project_qs)


class ChoiceCollection(UserResource):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)

    choice_set: models.QuerySet['Choice']

    class Meta:
        unique_together = ('questionnaire', 'name')


class Choice(models.Model):
    collection = models.ForeignKey(ChoiceCollection, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)  # (list name) Should be unique within ChoiceCollection
    label = models.CharField(max_length=255)
    geometry = gid_models.GeometryField(null=True, blank=True)

    class Meta:
        unique_together = ('collection', 'name')


class QuestionGroup(UserResource):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    relevant = models.CharField(max_length=255)  # ${has_child} = 'yes'
    # # Repeat attributes
    # is_repeat = models.BooleanField(default=False)
    # repeat_count = models.CharField(max_length=255)  # Eg: static: 3, formula: ${num_hh_members}

    class Meta:
        unique_together = ('questionnaire', 'name')


class Question(UserResource):
    class Type(models.IntegerChoices):
        # https://xlsform.org/en/#question-types

        INTEGER = 1, 'Integer (i.e., whole number) input.'
        DECIMAL = 2, 'Decimal input.'
        TEXT = 3, 'Free text response.'
        SELECT_ONE = 4, 'Multiple choice question; only one answer can be selected.'
        SELECT_MULTIPLE = 5, 'Multiple choice question; multiple answers can be selected.'
        RANK = 6, 'Rank question; order a list.'
        RANGE = 7, 'Range input (including rating)'
        # SELECT_ONE_FROM_FILE = 8, 'Multiple choice from file; only one answer can be selected.'
        # SELECT_MULTIPLE_FROM_FILE = 9, 'Multiple choice from file; multiple answers can be selected.'
        NOTE = 10, 'Display a note on the screen, takes no input. Shorthand for type=text with readonly=true.'
        # GEOPOINT = 11, 'Collect a single GPS coordinate.'
        # GEOTRACE = 12, 'Record a line of two or more GPS coordinates.'
        # GEOSHAPE = 13, 'Record a polygon of multiple GPS coordinates; the last point is the same as the first point.'
        DATE = 14, 'Date input.'
        TIME = 15, 'Time input.'
        DATETIME = 16, 'Accepts a date and a time input.'
        IMAGE = 17, 'Take a picture or upload an image file.'
        AUDIO = 18, 'Take an audio recording or upload an audio file.'
        # BACKGROUND_AUDIO = 19, 'Audio is recorded in the background while filling the form.'
        VIDEO = 20, 'Take a video recording or upload a video file.'
        FILE = 21, 'Generic file input (txt, pdf, xls, xlsx, doc, docx, rtf, zip)'
        BARCODE = 22, 'Scan a barcode, requires the barcode scanner app to be installed.'
        # CALCULATE = 23, 'Perform a calculation; see the Calculation section below.'
        ACKNOWLEDGE = 24, 'Acknowledge prompt that sets value to "OK" if selected.'
        # HIDDEN = 25, 'A field with no associated UI element which can be used to store a constant'
        # XML_EXTERNAL = 26, 'Adds a reference to an external XML data file'

    FIELDS_WITH_CHOICE_COLLECTION = {
        Type.SELECT_ONE,
        Type.SELECT_MULTIPLE,
        Type.RANK,
    }

    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    group = models.ForeignKey(QuestionGroup, on_delete=models.CASCADE, null=True, blank=True)
    type = models.PositiveSmallIntegerField(choices=Type.choices)

    # XXX: This needs to be also unique within Questionnaire & Question Bank
    name = models.CharField(max_length=255, validators=[validate_xlsform_name])
    label = models.TextField()
    choice_collection = models.ForeignKey(
        ChoiceCollection,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    hint = models.TextField(blank=True)

    # NOTE: Need to check if TextField or CharField should be used
    # default = models.TextField(blank=True)
    # guidance_hint = models.TextField(blank=True)
    # trigger = models.CharField(max_length=255, blank=True)
    # readonly = models.CharField(max_length=255, blank=True)
    # required = models.BooleanField(default=False)
    # required_message = models.CharField(max_length=255, blank=True)
    # relevant = models.CharField(max_length=255, blank=True)
    # constraint = models.CharField(max_length=255, blank=True)
    # appearance = models.CharField(max_length=255, blank=True)
    # calculation = models.CharField(max_length=255, blank=True)
    # parameters = models.CharField(max_length=255, blank=True)
    # choice_filter = models.CharField(max_length=255, blank=True)
    # image = models.CharField(max_length=255, blank=True)
    # video = models.CharField(max_length=255, blank=True)
    # -- Or Other
    # is_or_other = models.BooleanField(default=False)
    # or_other_label = models.TextField(blank=True)

    class Meta:
        unique_together = ('questionnaire', 'name')
