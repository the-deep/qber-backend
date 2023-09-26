import typing

from django.db import models
from django.core.exceptions import ValidationError

from utils.common import validate_xlsform_name


# Base Classes
class BaseChoiceCollection(models.Model):
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)

    class Meta:
        abstract = True


class BaseChoice(models.Model):
    name = models.CharField(max_length=255)  # (list name) Should be unique within ChoiceCollection
    label = models.CharField(max_length=255)
    # geometry = gid_models.GeometryField(null=True, blank=True)

    class Meta:
        abstract = True


class BaseQuestionLeafGroup(models.Model):
    class Type(models.IntegerChoices):
        MATRIX_1D = 1, 'Matrix 1D'
        MATRIX_2D = 2, 'Matrix 2D'

    class Category1(models.IntegerChoices):
        # MATRIX 1D (ROWS)
        CONTEXT = 101, 'Context'
        EVENT_AND_SHOCK = 102, 'Event and shock'
        DISPLACEMENT = 103, 'Displacement'
        CASUALTIES = 104, 'Casualties'
        INFORMATION_AND_COMMUNICATION = 105, 'Information and communication'
        HUMANITARIAN_ACCESS = 106, 'Humanitarian access'
        INTRODUCTION = 107, 'Introduction'
        CONCLUSION = 108, 'Conclusion'

        # Matrix 2D (ROWS) - Pillar
        IMPACT = 201, 'Impact'
        HUMANITARIAN_CONDITION = 202, 'Humanitarian condition'
        AT_RISK = 203, 'At Risk'
        PRIORITY_NEEDS = 204, 'Priority needs'
        PRIORITY_INTERVENTIONS = 205, 'Priority Interventions'
        CAPACITIES_AND_RESPONSE = 206, 'Capacities and response'

    class Category2(models.IntegerChoices):
        # MATRIX 1D (SUB-ROWS)
        # -- CONTEXT
        POLITICS = 10001, 'Politics'
        ECONOMICS = 10002, 'Economics'
        ENVIRONMENT = 10003, 'Environment'
        SOCIO_CULTURAL = 10004, 'Socio-cultural'
        DEMOGRAPHIC = 10005, 'Demographic'
        SECURITY_AND_STABILITY = 10006, 'Security and stability'
        # -- EVENT_AND_SHOCK
        TYPE_AND_CHARACTERISTICS = 10101, 'Type and characteristics'
        AGGRAVATING_FACTORS = 10102, 'Aggravating factors'
        MITIGATING_FACTORS = 10103, 'Mitigating factors'
        HAZARDS_AND_THREATS = 10104, 'Hazards & threats'
        # -- DISPLACEMENT
        DISPLACEMENT_CHARACTERISTICS = 10201, 'Displacement characteristics'
        PULL_FACTORS = 10202, 'Pull factors'
        PUSH_FACTORS = 10203, 'Push factors'
        INTENTIONS = 10204, 'Intentions'
        LOCAL_INTEGRATION = 10205, 'Local integration'
        # -- CASUALTIES
        DEAD = 10301, 'Dead'
        INJURED = 10302, 'Injured'
        MISSING = 10303, 'Missing'
        # -- INFORMATION_AND_COMMUNICATION
        COMMUNICATION_SOURCES_AND_MEANS = 10401, 'Communication sources and means'
        INFORMATION_CHALLENGES_AND_BARRIERS = 10402, 'Information challenges and barriers'
        KNOWLEDGE_AND_INFO_GAPS_POP = 10403, 'Knowledge and info gaps (Pop)'
        KNOWLEDGE_AND_INFO_GAPS_HUM = 10404, 'Knowledge and info gaps (Hum)'
        # -- HUMANITARIAN_ACCESS
        POPULATION_TO_RELIEF = 10501, 'Population to relief'
        RELIEF_TO_POPULATION = 10502, 'Relief to population'
        PHYSICAL_CONSTRAINTS = 10503, 'Physical constraints'
        SECURITY_CONSTRAINTS = 10504, 'Security constraints'
        PEOPLE_FACING_HUMANITARIAN_ACCESS_CONSTRAINT_HUMANITARIAN_ACCESS_GAPS = (
            10505,
            'People facing humanitarian access constraints/Humanitarian access gaps'
        )
        # -- Introduction
        INTRODUCTION = 10601, 'Introduction'
        QUESTIONNAIRE_CHARACTERISTICS = 10602, 'Questionnaire characteristics'
        ENUMERATOR_CHARACTERISTICS = 10603, 'Enumerator characteristics'
        RESPONDENT_CHARACTERISTICS = 10604, 'Respondent characteristics'
        AREA_CHARACTERISTICS = 10605, 'Area characteristics'
        AFFECTED_GROUP_CHARACTERISTICS = 10606, 'Affected group characteristics'
        # -- Conclusion
        CROSS = 10701, 'Cross'

        # Matrix 2D (Sub-ROWS) - Sub-Pillar
        # -- Impact
        DRIVERS = 20001, 'Drivers'
        IMPACT_ON_PEOPLE = 20002, 'Impact on people'
        IMPACT_ON_SYSTEMS_SERVICES_AND_NETWORKS = 20003, 'Impact on systems, services and networks'
        NUMBER_OF_PEOPLE_AFFECTED = 20004, 'Number of people affected'
        # -- Humanitarian condition
        LIVING_STANDARDS = 20101, 'Living standards'
        COPING_MECHANISMS = 20102, 'Coping mechanisms'
        PHYSICAL_AND_MENTAL_WELL_BEING = 20103, 'Physical and mental well being'
        NUMBER_OF_PEOPLE_IN_NEED = 20104, 'Number of people in need'
        # -- At Risk
        PEOPLE_AT_RISK = 20201, 'People at risk'
        NUMBER_OF_PEOPLE_AT_RISK = 20202, 'Number of people at risk'
        # -- Priority needs / Priority interventions
        EXPRESSED_BY_POPULATION = 20301, 'Expressed by population'
        EXPRESSED_BY_HUMANITARIAN_STAFF = 20302, 'Expressed by humanitarian staff'
        # -- Capacities and response XXX: Using 205XX in case we need saperate ENUM for Priority interventions
        GOVERNMENT_AND_LOCAL_AUTHORITIES = 20501, 'Government and local authorities'
        INTERNATIONAL_ORGANIZATIONS = 20502, 'International organizations'
        NATIONAL_AND_LOCAL_ORGANIZATIONS = 20503, 'National and local organizations'
        RED_CROSS_RED_CRESCENT = 20504, 'Red cross Red Crescent'
        HUMANITARIAN_COORDINATION = 20505, 'Humanitarian coordination'
        PEOPLE_REACHED_AND_RESPONSE_GAPS = 20506, 'People reached and response gaps'

    class Category3(models.IntegerChoices):
        # MATRIX 2D (SUB-COLUMNS) - Sector
        CROSS = 1000, 'Cross'
        HEALTH = 1001, 'Health'
        WASH = 1002, 'WASH'
        SHELTER = 1003, 'Shelter'
        FOOD_SECURITY = 1004, 'Food security'
        LIVELIHOODS = 1005, 'Livelihoods'
        NUTRITION = 1006, 'Nutrition'
        EDUCATION = 1007, 'Education'
        PROTECTION = 1008, 'Protection'
        AGRICULTURE = 1009, 'Agriculture'
        LOGISTIC = 1010, 'Logistic'

    class Category4(models.IntegerChoices):
        # MATRIX 2D (SUB-COLUMNS) - Sub Sector
        # -- Cross
        CROSS = 10001, 'Cross'
        # -- Health
        HEALTH_CARE = 10101, 'Health care'
        HEALTH_STATUS = 10102, 'Health status'
        # -- WASH
        WATER_SUPPLY = 10201, 'Water supply'
        excreta_management_sanitation = 10202, 'Excreta management /sanitation'
        SOLID_WASTE_MANAGEMENT = 10203, 'Solid waste management'
        HYGIENE_FACILITIES_AND_PRODUCTS = 10204, 'Hygiene facilities and products'
        WASH_IN_SCHOOLS = 10205, 'WASH in schools'
        WASH_IN_HEALTH_CARE_FACILITIES = 10206, 'WASH in health care facilities'
        VECTOR_CONTROL = 10207, 'Vector control'
        # -- Shelter
        DWELLING_ENVELOPE = 10301, 'Dwelling envelope'
        DOMESTIC_LIVING_SPACE = 10302, 'Domestic living space'
        NON_FOOD_HOUSEHOLD_ITEMS = 10303, 'Non-food household items'
        HOUSING_LAND_AND_PROPERTY_HLP = 10304, 'Housing, Land and Property (HLP)'
        SETTLEMENT = 10305, 'Settlement'
        # -- Food security
        FOOD = 10401, 'Food'
        NON_FOOD_ITEMS = 10402, 'Non Food Items'
        # -- Livelihoods
        NATURAL_CAPITAL = 10501, 'Natural capital'
        HUMAN_CAPITAL = 10502, 'Human capital'
        SOCIAL_CAPITAL = 10503, 'Social capital'
        PHYSICAL_CAPITAL = 10504, 'Physical capital'
        FINANCIAL_CAPITAL = 10505, 'Financial capital'
        OCCUPATION = 10506, 'Occupation'
        # -- Nutrition
        NUTRITION_STATUS = 10601, 'Nutrition status'
        NUTRITION_SERVICES = 10602, 'Nutrition services'
        # -- Education
        PROVISION = 10701, 'Provision'
        LEARNING_ENVIRONMENT = 10702, 'Learning environment'
        TEACHING_AND_LEARNING = 10703, 'Teaching and learning'
        TEACHERS_AND_OTHER_EDUCATION_PERSONNEL = 10704, 'Teachers and other education personnel'
        EDUCATION_POLICY = 10705, 'Education policy'
        # -- Protection
        DOCUMENTATION = 10801, 'Documentation'
        HUMAN_CIVIL_AND_POLITICAL_RIGHTS = 10802, 'Human, civil and political rights'
        JUSTICE_AND_RULE_OF_LAW = 10803, 'Justice and rule of law'
        PHYSICAL_SAFETY_AND_SECURITY = 10804, 'Physical safety and security'
        FREEDOM_OF_MOVEMENT = 10805, 'Freedom of movement'
        CHILD_PROTECTION = 10806, 'Child Protection'
        SEXUAL_AND_GENDER_BASED_VIOLENCE = 10807, 'Sexual and Gender-Based Violence'
        # XXX: HOUSING_LAND_AND_PROPERTY_HLP Use Shelter - HOUSING_LAND_AND_PROPERTY_HLP
        MINES_UXOS_AND_IEDS = 10809, 'Mines, UXOS and IEDs'
        # -- Agriculture
        PRODUCTION = 10901, 'Production'
        AGRICULTURAL_INPUTS = 10902, 'Agricultural inputs'
        AGRICULTURAL_INFRASTRUCTURE = 10903, 'Agricultural infrastructure'
        NATURAL_RESOURCE_MANAGEMENT = 10904, 'Natural resource management'
        # -- Logistic
        TRANSPORT = 11001, 'Transport'
        INFORMATION_AND_COMMUNICATION_TECHNOLOGIES_ICT = 11002, 'Information and communication technologies (ICT)'
        ENERGY = 11003, 'Energy'

    TYPE_CATEGORY_MAP = {
        Type.MATRIX_1D: {
            Category1.CONTEXT: {
                Category2.POLITICS,
                Category2.ECONOMICS,
                Category2.ENVIRONMENT,
                Category2.SOCIO_CULTURAL,
                Category2.DEMOGRAPHIC,
                Category2.SECURITY_AND_STABILITY,
            },
            Category1.EVENT_AND_SHOCK: {
                Category2.TYPE_AND_CHARACTERISTICS,
                Category2.AGGRAVATING_FACTORS,
                Category2.MITIGATING_FACTORS,
                Category2.HAZARDS_AND_THREATS,
            },
            Category1.DISPLACEMENT: {
                Category2.DISPLACEMENT_CHARACTERISTICS,
                Category2.PULL_FACTORS,
                Category2.PUSH_FACTORS,
                Category2.INTENTIONS,
                Category2.LOCAL_INTEGRATION,
            },
            Category1.CASUALTIES: {
                Category2.DEAD,
                Category2.INJURED,
                Category2.MISSING,
            },
            Category1.INFORMATION_AND_COMMUNICATION: {
                Category2.COMMUNICATION_SOURCES_AND_MEANS,
                Category2.INFORMATION_CHALLENGES_AND_BARRIERS,
                Category2.KNOWLEDGE_AND_INFO_GAPS_POP,
                Category2.KNOWLEDGE_AND_INFO_GAPS_HUM,
            },
            Category1.HUMANITARIAN_ACCESS: {
                Category2.POPULATION_TO_RELIEF,
                Category2.RELIEF_TO_POPULATION,
                Category2.PHYSICAL_CONSTRAINTS,
                Category2.SECURITY_CONSTRAINTS,
                Category2.PEOPLE_FACING_HUMANITARIAN_ACCESS_CONSTRAINT_HUMANITARIAN_ACCESS_GAPS,
            },
        },

        Type.MATRIX_2D: {
            # rows: sub-rows <-> pillar: sub-pillar
            'rows': {
                Category1.IMPACT: {
                    Category2.DRIVERS,
                    Category2.IMPACT_ON_PEOPLE,
                    Category2.IMPACT_ON_SYSTEMS_SERVICES_AND_NETWORKS,
                    Category2.NUMBER_OF_PEOPLE_AFFECTED,
                },
                Category1.HUMANITARIAN_CONDITION: {
                    Category2.LIVING_STANDARDS,
                    Category2.COPING_MECHANISMS,
                    Category2.PHYSICAL_AND_MENTAL_WELL_BEING,
                    Category2.NUMBER_OF_PEOPLE_IN_NEED,
                },
                Category1.AT_RISK: {
                    Category2.PEOPLE_AT_RISK,
                    Category2.NUMBER_OF_PEOPLE_AT_RISK,
                },
                Category1.PRIORITY_NEEDS: {
                    Category2.EXPRESSED_BY_POPULATION,
                    Category2.EXPRESSED_BY_HUMANITARIAN_STAFF,
                },
                Category1.PRIORITY_INTERVENTIONS: {
                    Category2.EXPRESSED_BY_POPULATION,
                    Category2.EXPRESSED_BY_HUMANITARIAN_STAFF,
                },
                Category1.CAPACITIES_AND_RESPONSE: {
                    Category2.GOVERNMENT_AND_LOCAL_AUTHORITIES,
                    Category2.INTERNATIONAL_ORGANIZATIONS,
                    Category2.NATIONAL_AND_LOCAL_ORGANIZATIONS,
                    Category2.RED_CROSS_RED_CRESCENT,
                    Category2.HUMANITARIAN_COORDINATION,
                    Category2.PEOPLE_REACHED_AND_RESPONSE_GAPS,
                },
            },
            # columns: sub-columns <-> sector: sub-sector
            'columns': {
                Category3.CROSS: {
                    Category4.CROSS,
                },
                Category3.HEALTH: {
                    Category4.HEALTH_CARE,
                    Category4.HEALTH_STATUS,
                },
                Category3.WASH: {
                    Category4.WATER_SUPPLY,
                    Category4.excreta_management_sanitation,
                    Category4.SOLID_WASTE_MANAGEMENT,
                    Category4.HYGIENE_FACILITIES_AND_PRODUCTS,
                    Category4.WASH_IN_SCHOOLS,
                    Category4.WASH_IN_HEALTH_CARE_FACILITIES,
                    Category4.VECTOR_CONTROL,
                },
                Category3.SHELTER: {
                    Category4.DWELLING_ENVELOPE,
                    Category4.DOMESTIC_LIVING_SPACE,
                    Category4.NON_FOOD_HOUSEHOLD_ITEMS,
                    Category4.HOUSING_LAND_AND_PROPERTY_HLP,
                    Category4.SETTLEMENT,
                },
                Category3.FOOD_SECURITY: {
                    Category4.FOOD,
                    Category4.NON_FOOD_ITEMS,
                },
                Category3.LIVELIHOODS: {
                    Category4.NATURAL_CAPITAL,
                    Category4.HUMAN_CAPITAL,
                    Category4.SOCIAL_CAPITAL,
                    Category4.PHYSICAL_CAPITAL,
                    Category4.FINANCIAL_CAPITAL,
                    Category4.OCCUPATION,
                },
                Category3.NUTRITION: {
                    Category4.NUTRITION_STATUS,
                    Category4.NUTRITION_SERVICES,
                },
                Category3.EDUCATION: {
                    Category4.PROVISION,
                    Category4.LEARNING_ENVIRONMENT,
                    Category4.TEACHING_AND_LEARNING,
                    Category4.TEACHERS_AND_OTHER_EDUCATION_PERSONNEL,
                    Category4.EDUCATION_POLICY,
                },
                Category3.PROTECTION: {
                    Category4.DOCUMENTATION,
                    Category4.HUMAN_CIVIL_AND_POLITICAL_RIGHTS,
                    Category4.JUSTICE_AND_RULE_OF_LAW,
                    Category4.PHYSICAL_SAFETY_AND_SECURITY,
                    Category4.FREEDOM_OF_MOVEMENT,
                    Category4.CHILD_PROTECTION,
                    Category4.SEXUAL_AND_GENDER_BASED_VIOLENCE,
                    Category4.HOUSING_LAND_AND_PROPERTY_HLP,
                    Category4.MINES_UXOS_AND_IEDS,
                },
                Category3.AGRICULTURE: {
                    Category4.PRODUCTION,
                    Category4.AGRICULTURAL_INPUTS,
                    Category4.AGRICULTURAL_INFRASTRUCTURE,
                    Category4.NATURAL_RESOURCE_MANAGEMENT,
                },
                Category3.LOGISTIC: {
                    Category4.TRANSPORT,
                    Category4.INFORMATION_AND_COMMUNICATION_TECHNOLOGIES_ICT,
                    Category4.ENERGY,
                },
            },
        }
    }

    # TODO: Make sure this is unique within questions and groups
    name = models.CharField(max_length=255)
    type = models.PositiveSmallIntegerField(choices=Type.choices)
    order = models.PositiveSmallIntegerField(default=0)

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
        abstract = True

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
        if self.type == self.Type.MATRIX_1D:
            if self.category_1 not in self.TYPE_CATEGORY_MAP[self.type]:
                raise ValidationError('Wrong category 1 provided for Matrix 1D')
            if self.category_2 not in self.TYPE_CATEGORY_MAP[self.type][self.category_1]:
                raise ValidationError('Wrong category 2 provided for Matrix 1D')
            if self.category_3 is not None or self.category_4 is not None:
                raise ValidationError('Category 3/4 are only for Matrix 2D')
        # Matrix 2D
        elif self.type == self.Type.MATRIX_2D:
            if self.category_1 not in self.TYPE_CATEGORY_MAP[self.type]['rows']:
                raise ValidationError('Wrong category 1 provided for Matrix 2D')
            if self.category_2 not in self.TYPE_CATEGORY_MAP[self.type]['rows'][self.category_1]:
                raise ValidationError('Wrong category 2 provided for Matrix 2D')
            if self.category_3 is None or self.category_4 is None:
                raise ValidationError('Category 3/4 needs to be defined for Matrix 2D')
            if self.category_3 not in self.TYPE_CATEGORY_MAP[self.type]['columns']:
                raise ValidationError('Wrong category 3 provided for Matrix 2D')
            if self.category_4 not in self.TYPE_CATEGORY_MAP[self.type]['columns'][self.category_3]:
                # TODO: Add support for nullable category 4
                raise ValidationError('Wrong category 4 provided for Matrix 2D')
        else:
            raise ValidationError(f'{self.type} Not implemented type')

    @property
    def existing_leaf_groups_qs(self) -> models.QuerySet[typing.Self]:
        raise Exception('Not implemented.')

    def save(self, *args, **kwargs):
        # NOTE: For now this is generated from system, so validating here
        self.clean()
        existing_leaf_groups_qs = self.existing_leaf_groups_qs
        if self.pk:
            existing_leaf_groups_qs = existing_leaf_groups_qs.exclude(pk=self.pk)
        # Matrix 1D
        if self.type == self.Type.MATRIX_1D:
            qs = existing_leaf_groups_qs.filter(
                category_1=self.category_1,
                category_2=self.category_2,
            )
            if qs.exists():
                raise ValidationError('Already exists')
        # Matrix 2D
        elif self.type == self.Type.MATRIX_2D:
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


class QberMetaData(models.Model):
    class PriorityLevel(models.IntegerChoices):
        HIGH = 1, 'High'
        MEDIUM = 2, 'Medium'
        LOW = 3, 'Low'

    class EnumeratorSkill(models.IntegerChoices):
        BASIC = 1, 'Basic'
        INTERMEDIATE = 2, 'Intermediate'
        ADVANCED = 3, 'Advanced'

    class DataCollectionMethod(models.IntegerChoices):
        # TODO: Incomplete
        DIRECT = 1, 'Direct observation'
        FOCUS_GROUP = 2, 'Focus group'
        ONE_ON_ONE_INTERVIEW = 3, '1-on-1 interviews'
        OPEN_ENDED_SURVEY = 4, 'Open-ended survey'
        CLOSED_ENDED_SURVEY = 5, 'Closed-ended survey'
        KEY_INFORMANT_INTERVIEW = 6, 'Key Informant Interview'
        AUTOMATIC = 7, 'Automatic'

    priority_level = models.PositiveSmallIntegerField(choices=PriorityLevel.choices, null=True, blank=True)
    enumerator_skill = models.PositiveSmallIntegerField(choices=EnumeratorSkill.choices, null=True, blank=True)
    data_collection_method = models.PositiveSmallIntegerField(choices=DataCollectionMethod.choices, null=True, blank=True)
    required_duration = models.PositiveIntegerField(null=True, blank=True, help_text='In seconds')

    class Meta:
        abstract = True


class BaseQuestion(QberMetaData):

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

    type = models.PositiveSmallIntegerField(choices=Type.choices)
    order = models.PositiveSmallIntegerField(default=0)

    # XXX: This needs to be also unique within Questionnaire & Question Bank
    # TODO: Make sure this is also unique within questions and groups
    name = models.CharField(max_length=255, validators=[validate_xlsform_name])
    label = models.TextField()

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
    constraint_message = models.CharField(max_length=255, blank=True)
    appearance = models.CharField(max_length=255, blank=True)
    calculation = models.CharField(max_length=255, blank=True)
    parameters = models.CharField(max_length=255, blank=True)
    choice_filter = models.CharField(max_length=255, blank=True)
    image = models.CharField(max_length=255, blank=True)
    video = models.CharField(max_length=255, blank=True)
    # -- Or Other: https://xlsform.org/en/#specify-other
    is_or_other = models.BooleanField(default=False)

    choice_collection_id: int

    """
    # NOTE: ForeignKey key required when used
    - choice_collection
    - leaf_group
    """

    class Meta:
        abstract = True
