import typing
from django.db import models
from django.contrib.gis.db import models as gid_models
from django.core.exceptions import ValidationError
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
    # qbank = models.ForeignKey('qbank.QuestionBank', on_delete=models.PROTECT)

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
    question_set: models.QuerySet['Question']

    def __str__(self):
        return self.title

    @classmethod
    def get_for(cls, user, queryset=None):
        project_qs = Project.get_for(user)
        return get_queryset_for_model(cls, queryset=queryset).filter(project__in=project_qs)

    def delete(self):
        # Delete questions first as question depends on other attributes which will through PROTECT error
        self.question_set.all().delete()
        return super().delete()


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


class QuestionLeafGroup(UserResource):
    # NOTE: Only created by system right now

    class Type(models.IntegerChoices):
        MATRIX_1D = 1, 'Matrix 1D'
        MATRIX_2D = 2, 'Matrix 2D'

    class Category1(models.IntegerChoices):
        # MATRIX 1D (ROWS)
        CONTEXT = 101, '1. Context'
        EVENT_SHOCK = 102, '2. Event/Shock'
        DISPLACEMENT = 103, '3. Displacement'
        CASUALTIES = 104, '4. Casualties'
        INFORMATION_AND_COMMUNICATION = 105, '5. Information And Communication'
        HUMANITARIAN_ACCESS = 106, '6. Humanitarian Access'
        # Matrix 2D (ROWS)
        IMPACT = 201, '7. Impact'
        HUMANITARIAN_CONDITIONS = 202, '8. Humanitarian Conditions'
        AT_RISK = 203, '9. At Risk'
        PRIORITIES = 204, '10. Priorities'
        CAPACITIES_RESPONSE = 205, '11. Capacities Response'

    class Category2(models.IntegerChoices):
        # MATRIX 1D (SUB-ROWS)
        # -- CONTEXT
        POLITICS = 1001, 'Politics'
        DEMOGRAPHY = 1002, 'Demography'
        SOCIO_CULTURAL = 1003, 'Socio Cultural'
        ENVIRONMENT = 1004, 'Environment'
        SECURITY_AND_STABILITY = 1005, 'Security And Stability'
        ECONOMICS = 1006, 'Economics'
        # -- EVENT_SHOCK
        EVENT_SHOCK_CHARACTERISTICS = 1101, 'Characteristics'
        DRIVERS_AND_AGGRAVATING_FACTORS = 1102, 'Drivers And Aggravating Factors'
        MITIGATING_FACTORS = 1103, 'Mitigating Factors'
        HAZARDS_AND_THREATS = 1104, 'Hazards And Threats'
        # -- DISPLACEMENT
        DISPLACEMENT_CHARACTERISTICS = 1201, 'Characteristics'
        PUSH_FACTORS = 1202, 'Push Factors'
        PULL_FACTORS = 1203, 'Pull Factors'
        INTENTIONS = 1204, 'Intentions'
        LOCAL_INTEGRATION = 1205, 'Local Integration'
        # -- CASUALTIES
        DEAD = 1301, 'Dead'
        INJURED = 1302, 'Injured'
        MISSING = 1303, 'Missing'
        # -- INFORMATION_AND_COMMUNICATION
        SOURCE_AND_MEANS = 1401, 'Source And Means'
        CHALLENDGES_AND_BARRIERS = 1402, 'Challendges And Barriers'
        KNOWLEDGE_AND_INFO_GAPS_HUMANITARIAN = 1403, 'Knowledge And Info Gaps (Humanitarian)'
        KNOWLEDGE_AND_INFO_GAPS_POPULATION = 1404, 'Knowledge And Info Gaps POPULATION)'
        # -- HUMANITARIAN_ACCESS
        POPULATION_TO_RELIEF = 1501, 'Population To Relief'
        RELIEF_TO_POPULATION = 1502, 'Relief To Population'
        PHYSICAL_AND_SECURITY = 1503, 'Physical And Security'
        NUMBER_OF_PEOPLE_FACING_HUMANITARIN_ACCESS_CONSTRAINTS = 1504, 'Number Of People Facing Hum. Access Constraints'
        # Matrix 2D (Sub-ROWS)
        # -- IMPACT
        DRIVERS = 2001, 'Drivers'
        IMPACT_ON_PEOPLE = 2002, 'Impact On People'
        IMPACT_ON_SYSTEMS_SERVICES_NETWORK = 2003, 'Impact On Systems Services Network'
        # -- HUMANITARIAN_CONDITIONS
        LIVING_STANDARDS = 2101, 'Living Standards'
        COPING_MECHANISMS = 2102, 'Coping Mechanisms'
        PHYSICAL_AND_MENTAL_WELLBEING = 2103, 'Physical And Mental Wellbeing'
        # -- AT_RISK
        PEOPLE_AT_RISK = 2201, 'People At risk'
        # -- PRIORITIES
        PRIOTIY_ISSUES_POP = 2301, 'Priotiy Issues (Pop)'
        PRIOTIY_ISSUES_HUM = 2302, 'Priotiy Issues (Hum)'
        PRIOTIY_INTERVENTIONS_POP = 2303, 'Priotiy Interventions (Pop)'
        PRIOTIY_INTERVENTIONS_HUM = 2304, 'Priotiy Interventions (Hum)'
        # -- CAPACITIES_RESPONSE
        GOVERNMENT_LOCAL_AUTHORITIES = 2401, 'Government Local Authorities'
        INTERNATIONAL_ORGANISATIONS = 2402, 'International Organisations'
        NATION_AND_LOCAL_ORGANISATIONS = 2403, 'Nation And Local Organisations'
        RED_CROSS_RED_CRESCENT = 2404, 'Red Cross Red Crescent'
        HUMANITARIAN_COORDINATION = 2405, 'Humanitarian Coordination'

    class Category3(models.IntegerChoices):
        # MATRIX 2D (SUB-COLUMNS)
        CROSS = 1001, 'Cross'
        FOOD = 1002, 'Food'
        WASH = 1003, 'Wash'
        HEALTH = 1004, 'Health'
        PROTECTION = 1005, 'Protection'
        EDUCATION = 1006, 'Education'
        LIVELIHOOD = 1007, 'Livelihood'
        NUTRITION = 1008, 'Nutrition'
        AGRICULTURE = 1009, 'Agriculture'
        LOGISTICS = 1010, 'Logistics'
        SHELTER = 1011, 'Shelter'
        ANALYTICAL_OUTPUTS = 1012, 'Analytical Outputs'

    class Category4(models.IntegerChoices):
        # MATRIX 2D (COLUMNS)
        # -- CROSS
        # -- FOOD
        # -- WASH
        WATER = 3001, 'Water'
        SANITATION = 3002, 'Sanitation'
        HYGIENE = 3003, 'Hygiene'
        WASTE_MANAGEMENT = 3004, 'Waste Management'
        VECTOR_CONTROL = 3005, 'Vector Control'
        # -- HEALTH
        HEALTH_CARE = 4001, 'Health Care'
        HEALTH_STATUS = 4002, 'Health Status'
        # -- PROTECTION
        DOCUMENTATION = 5001, 'Documentation'
        CIVIL_AND_POLITICAL_RIGHTS = 5002, 'Civil And Political Rights'
        PHYSICAL_SAFETY_AND_SECURITY = 5003, 'Physical Safety And Security'
        FREEDOM_OF_MOVEMENT = 5004, 'Freedom Of Movement'
        LIBERTY = 5005, 'Liberty'
        CHILD_PROTECTION = 5006, 'Child Protection'
        SGBV = 5007, 'SGBV'
        HOUSING_LAND_AND_PROPERTY = 5008, 'housing Land And Property'
        JUSTICE_AND_RULE_OF_LAW = 5009, 'Justice And Rule Of Law'
        MINES = 5010, 'MINES'
        HUMAN_TRAFFICKING = 5011, 'Human Trafficking'
        # -- EDUCATION
        LEARNING_ENVIRONMENT = 6001, 'Learning Environment'
        FACILITIES_AND_AMENITIES = 6002, 'Facilities And Amenities'
        TEACHER_AND_LEARNING = 6003, 'Teacher And Learning'
        TEACHERS_AND_EDUCATION_PERSONNEL = 6004, 'Teachers And Education Personnel'
        # -- LIVELIHOOD
        INCOME = 7001, 'Income'
        EXPENDITURES = 7002, 'Expenditures'
        PRODUCTIVE_ASSETS = 7003, 'Productive Assets'
        SKILLS_AND_QUALIFICATIONS = 7004, 'Skills And Qualifications'
        # -- NUTRITION
        NUTRITION_GOODS_AND_SERVICES = 8001, 'Nutrition Goods And Services'
        NUTRITION_STATUS = 8002, 'Nutrition Status'
        # -- AGRICULTURE
        # -- LOGISTICS
        # -- SHELTER
        DWELLING_ENVELOPPE = 12001, 'Dwelling Enveloppe'
        INTERIOR_DOMENSTIC_LIFE = 12002, 'Interior Domenstic Life'
        # -- ANALYTICAL_OUTPUTS

    TYPE_CATEGORY_MAP = {
        Type.MATRIX_1D: {
            Category1.CONTEXT: {
                Category2.POLITICS,
                Category2.DEMOGRAPHY,
                Category2.SOCIO_CULTURAL,
                Category2.ENVIRONMENT,
                Category2.SECURITY_AND_STABILITY,
                Category2.ECONOMICS,
            },
            Category1.EVENT_SHOCK: {
                Category2.EVENT_SHOCK_CHARACTERISTICS,
                Category2.DRIVERS_AND_AGGRAVATING_FACTORS,
                Category2.MITIGATING_FACTORS,
                Category2.HAZARDS_AND_THREATS,
            },
            Category1.DISPLACEMENT: {
                Category2.DISPLACEMENT_CHARACTERISTICS,
                Category2.PUSH_FACTORS,
                Category2.PULL_FACTORS,
                Category2.INTENTIONS,
                Category2.LOCAL_INTEGRATION,
            },
            Category1.CASUALTIES: {
                Category2.DEAD,
                Category2.INJURED,
                Category2.MISSING,
            },
            Category1.INFORMATION_AND_COMMUNICATION: {
                Category2.SOURCE_AND_MEANS,
                Category2.CHALLENDGES_AND_BARRIERS,
                Category2.KNOWLEDGE_AND_INFO_GAPS_HUMANITARIAN,
                Category2.KNOWLEDGE_AND_INFO_GAPS_POPULATION,
            },
            Category1.HUMANITARIAN_ACCESS: {
                Category2.POPULATION_TO_RELIEF,
                Category2.RELIEF_TO_POPULATION,
                Category2.PHYSICAL_AND_SECURITY,
                Category2.NUMBER_OF_PEOPLE_FACING_HUMANITARIN_ACCESS_CONSTRAINTS,
            },
        },
        Type.MATRIX_2D: {
            # rows: sub-rows
            'rows': {
                Category1.IMPACT: {
                    Category2.DRIVERS,
                    Category2.IMPACT_ON_PEOPLE,
                    Category2.IMPACT_ON_SYSTEMS_SERVICES_NETWORK,
                },
                Category1.HUMANITARIAN_CONDITIONS: {
                    Category2.LIVING_STANDARDS,
                    Category2.COPING_MECHANISMS,
                    Category2.PHYSICAL_AND_MENTAL_WELLBEING,
                },
                Category1.AT_RISK: {
                    Category2.PEOPLE_AT_RISK,
                },
                Category1.PRIORITIES: {
                    Category2.PRIOTIY_ISSUES_POP,
                    Category2.PRIOTIY_ISSUES_HUM,
                    Category2.PRIOTIY_INTERVENTIONS_POP,
                    Category2.PRIOTIY_INTERVENTIONS_HUM,
                },
                Category1.CAPACITIES_RESPONSE: {
                    Category2.GOVERNMENT_LOCAL_AUTHORITIES,
                    Category2.INTERNATIONAL_ORGANISATIONS,
                    Category2.NATION_AND_LOCAL_ORGANISATIONS,
                    Category2.RED_CROSS_RED_CRESCENT,
                    Category2.HUMANITARIAN_COORDINATION,
                },
            },
            # columns: sub-columns
            'columns': {
                Category3.CROSS: {},
                Category3.FOOD: {},
                Category3.WASH: {
                    Category4.WATER,
                    Category4.SANITATION,
                    Category4.HYGIENE,
                    Category4.WASTE_MANAGEMENT,
                    Category4.VECTOR_CONTROL,
                },
                Category3.HEALTH: {
                    Category4.HEALTH_CARE,
                    Category4.HEALTH_STATUS,
                },
                Category3.PROTECTION: {
                    Category4.DOCUMENTATION,
                    Category4.CIVIL_AND_POLITICAL_RIGHTS,
                    Category4.PHYSICAL_SAFETY_AND_SECURITY,
                    Category4.FREEDOM_OF_MOVEMENT,
                    Category4.LIBERTY,
                    Category4.CHILD_PROTECTION,
                    Category4.SGBV,
                    Category4.HOUSING_LAND_AND_PROPERTY,
                    Category4.JUSTICE_AND_RULE_OF_LAW,
                    Category4.MINES,
                    Category4.HUMAN_TRAFFICKING,
                },
                Category3.EDUCATION: {
                    Category4.LEARNING_ENVIRONMENT,
                    Category4.FACILITIES_AND_AMENITIES,
                    Category4.TEACHER_AND_LEARNING,
                    Category4.TEACHERS_AND_EDUCATION_PERSONNEL,
                },
                Category3.LIVELIHOOD: {
                    Category4.INCOME,
                    Category4.EXPENDITURES,
                    Category4.PRODUCTIVE_ASSETS,
                    Category4.SKILLS_AND_QUALIFICATIONS,
                },
                Category3.NUTRITION: {
                    Category4.NUTRITION_GOODS_AND_SERVICES,
                    Category4.NUTRITION_STATUS,
                },
                Category3.AGRICULTURE: {},
                Category3.LOGISTICS: {},
                Category3.SHELTER: {
                    Category4.DWELLING_ENVELOPPE,
                    Category4.INTERIOR_DOMENSTIC_LIFE,
                },
                Category3.ANALYTICAL_OUTPUTS: {},
            },
        }
    }

    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    # TODO: Make sure this is unique within questions and groups
    name = models.CharField(max_length=255)
    type = models.PositiveSmallIntegerField(choices=Type.choices)
    order = models.PositiveSmallIntegerField(default=0)
    is_hidden = models.BooleanField(default=False)

    # Categories
    # TODO: UNIQUE CHECK
    # -- For Matrix1D/Matrix2D
    category_1 = models.PositiveSmallIntegerField(choices=Category1.choices)
    category_2 = models.PositiveSmallIntegerField(choices=Category2.choices)
    # -- For Matrix2D
    category_3 = models.PositiveSmallIntegerField(choices=Category3.choices, null=True, blank=True)
    category_4 = models.PositiveSmallIntegerField(choices=Category4.choices, null=True, blank=True)

    # Misc
    relevant = models.CharField(max_length=255, blank=True)  # ${has_child} = 'yes'

    # Dynamic Types
    get_type_display: typing.Callable[[], str]
    get_category_1_display: typing.Callable[[], str]
    get_category_2_display: typing.Callable[[], str]
    get_category_3_display: typing.Callable[[], typing.Optional[str]]
    get_category_4_display: typing.Callable[[], typing.Optional[str]]

    class Meta:
        unique_together = [
            ('questionnaire', 'name'),
            ('questionnaire', 'category_1', 'category_2', 'category_3', 'category_4'),
        ]
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['order']),
        ]
        ordering = ('order',)

    def __str__(self):
        if self.type == self.Type.MATRIX_1D:
            return '::'.join([
                self.get_category_1_display(),
                self.get_category_2_display(),
            ])
        return '::'.join([
            self.get_category_1_display(),
            self.get_category_2_display(),
            self.get_category_3_display() or '-',
            self.get_category_4_display() or '-',
        ])

    def clean(self):
        # NOTE: For now this is generated from system, so validating here
        # Matrix 1D
        if self.type == QuestionLeafGroup.Type.MATRIX_1D:
            if self.category_1 not in QuestionLeafGroup.TYPE_CATEGORY_MAP[self.type]:
                raise ValidationError('Wrong category 1 provided for Matrix 1D')
            if self.category_2 not in QuestionLeafGroup.TYPE_CATEGORY_MAP[self.type][self.category_1]:
                raise ValidationError('Wrong category 2 provided for Matrix 1D')
            if self.category_3 is not None or self.category_4 is not None:
                raise ValidationError('Category 3/4 are only for Matrix 2D')
        # Matrix 2D
        elif self.type == QuestionLeafGroup.Type.MATRIX_2D:
            if self.category_1 not in QuestionLeafGroup.TYPE_CATEGORY_MAP[self.type]['rows']:
                raise ValidationError('Wrong category 1 provided for Matrix 2D')
            if self.category_2 not in QuestionLeafGroup.TYPE_CATEGORY_MAP[self.type]['rows'][self.category_1]:
                raise ValidationError('Wrong category 2 provided for Matrix 2D')
            if self.category_3 is None or self.category_4 is None:
                raise ValidationError('Category 3/4 needs to be defined for Matrix 2D')
            if self.category_3 not in QuestionLeafGroup.TYPE_CATEGORY_MAP[self.type]['columns']:
                raise ValidationError('Wrong category 3 provided for Matrix 2D')
            if self.category_4 not in QuestionLeafGroup.TYPE_CATEGORY_MAP[self.type]['columns'][self.category_3]:
                # TODO: Add support for nullable category 4
                raise ValidationError('Wrong category 4 provided for Matrix 2D')
        else:
            raise ValidationError('Not implemented type')

    def save(self, *args, **kwargs):
        # NOTE: For now this is generated from system, so validating here
        self.clean()
        existing_leaf_groups_qs = QuestionLeafGroup.objects.filter(
            # Scope by questionnaire
            questionnaire=self.questionnaire,
        )
        if self.pk:
            existing_leaf_groups_qs = existing_leaf_groups_qs.exclude(pk=self.pk)
        # Matrix 1D
        if self.type == QuestionLeafGroup.Type.MATRIX_1D:
            qs = existing_leaf_groups_qs.filter(
                category_1=self.category_1,
                category_2=self.category_2,
            )
            if qs.exists():
                raise ValidationError('Already exists')
        # Matrix 2D
        elif self.type == QuestionLeafGroup.Type.MATRIX_2D:
            qs = existing_leaf_groups_qs.filter(
                category_1=self.category_1,
                category_2=self.category_2,
                category_3=self.category_3,
                category_4=self.category_4,
            )
            if qs.exists():
                raise ValidationError('Already exists')
        else:
            raise ValidationError('Not implemented type')
        return super().save(*args, **kwargs)


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
    leaf_group = models.ForeignKey(QuestionLeafGroup, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(choices=Type.choices)
    order = models.PositiveSmallIntegerField(default=0)

    # XXX: This needs to be also unique within Questionnaire & Question Bank
    # TODO: Make sure this is also unique within questions and groups
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
    default = models.TextField(blank=True)
    guidance_hint = models.TextField(blank=True)
    trigger = models.CharField(max_length=255, blank=True)
    readonly = models.CharField(max_length=255, blank=True)
    required = models.BooleanField(default=False)
    required_message = models.CharField(max_length=255, blank=True)
    relevant = models.CharField(max_length=255, blank=True)
    constraint = models.CharField(max_length=255, blank=True)
    appearance = models.CharField(max_length=255, blank=True)
    calculation = models.CharField(max_length=255, blank=True)
    parameters = models.CharField(max_length=255, blank=True)
    choice_filter = models.CharField(max_length=255, blank=True)
    image = models.CharField(max_length=255, blank=True)
    video = models.CharField(max_length=255, blank=True)
    # -- Or Other: https://xlsform.org/en/#specify-other
    is_or_other = models.BooleanField(default=False)
    or_other_label = models.TextField(blank=True)

    class Meta:
        unique_together = ('questionnaire', 'name')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['order']),
        ]
        ordering = ('leaf_group__order', 'order',)
