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
        SHOCKS_AND_EVENTS = 102, 'Shocks and events'
        DISPLACEMENT = 103, 'Displacement'
        CASUALTIES = 104, 'Casualties'
        INFORMATION_AND_COMMUNICATION = 105, 'Information and communication'
        HUMANITARIAN_ACCESS = 106, 'Humanitarian access'
        INTRODUCTION = 107, 'Introduction'
        CONCLUSION = 108, 'Conclusion'
        MARKET = 109, 'Market'

        # Matrix 2D (ROWS) - Pillar
        IMPACT = 201, 'Impact'
        HUMANITARIAN_CONDITION = 202, 'Humanitarian condition'
        AT_RISK = 203, 'At Risk'
        PRIORITIES_AND_PREFERENCES = 204, 'Priorities and preferences'
        CAPACITIES_AND_RESPONSE = 205, 'Capacities and response'

    class Category2(models.IntegerChoices):
        # MATRIX 1D (SUB-ROWS)
        # -- CONTEXT
        INTRODUCTION = 10101, 'Introduction'
        POLITICS = 10102, 'Politics'
        ECONOMICS = 10103, 'Economics'
        ENVIRONMENT = 10104, 'Environment'
        SOCIO_CULTURAL = 10105, 'Socio-cultural'
        DEMOGRAPHICS = 10106, 'Demographics'
        SECURITY_AND_STABILITY = 10107, 'Security and stability'
        # -- SHOCKS_AND_EVENTS
        # -- -- CONTEXT - INTRODUCTION
        TYPE_AND_CHARACTERISTICS = 10201, 'Type and characteristics'
        AGGRAVATING_FACTORS = 10202, 'Aggravating factors'
        MITIGATING_FACTORS = 10203, 'Mitigating factors'
        THREATS_AND_HAZARDS = 10204, 'Threats and hazards'
        # -- DISPLACEMENT
        INTRODUCTION_PEOPLE_ARRIVING = 10301, 'Introduction people arriving'
        INTRODUCTION_PEOPLE_LEAVING = 10302, 'Introduction people leaving'
        # -- -- CONTEXT - TYPE_AND_CHARACTERISTICS
        PULL_FACTORS = 10304, 'Pull factors'
        PUSH_FACTORS = 10305, 'Push factors'
        INTENTIONS = 10306, 'Intentions'
        LOCAL_INTEGRATION = 10307, 'Local integration'
        # -- CASUALTIES
        # -- -- CONTEXT - INTRODUCTION
        CROSS = 10401, 'Cross'
        DEAD = 10402, 'Dead'
        INJURED = 10403, 'Injured'
        MISSING = 10404, 'Missing'
        # -- INFORMATION_AND_COMMUNICATION
        # -- -- CONTEXT - INTRODUCTION
        # -- -- CASUALTIES - CROSS
        COMMUNICATION_SOURCES_AND_MEANS = 10501, 'Communication sources and means'
        CHALLENGES_AND_BARRIERS = 10502, 'Challenges and barriers'
        KNOWLEDGE_AND_INFORMATION_GAPS_POPULATION = 10503, 'Knowledge and information gaps (population)'
        KNOWLEDGE_AND_INFORMATION_GAPS_HUMANITARIANS = 10504, 'Knowledge and information gaps (humanitarians)'
        # -- HUMANITARIAN_ACCESS
        INTRODUCTION_HUMANITARIAN_ACTORS_BARRIERS = 10601, 'Introduction humanitarian actors barriers'
        INTRODUCTION_PEOPLE_AFFECTED_BARRIERS = 10602, 'Introduction people affected barriers'
        POPULATION_TO_RELIEF = 10603, 'Population to relief'
        RELIEF_TO_POPULATION = 10604, 'Relief to population'
        PHYSICAL_AND_SECURITY_CONSTRAINTS = 10605, 'Physical and security constraints'
        PEOPLE_FACING_HUMANITARIAN_ACCESS_CONSTRAINT_HUMANITARIAN_ACCESS_GAPS = (
            10606,
            'People facing humanitarian access constraints/Humanitarian access gaps'
        )
        # -- Introduction
        # -- -- CONTEXT - INTRODUCTION
        QUESTIONNAIRE_CHARACTERISTICS = 10701, 'Questionnaire characteristics'
        ENUMERATOR_CHARACTERISTICS = 10702, 'Enumerator characteristics'
        RESPONDENT_CHARACTERISTICS = 10703, 'Respondent characteristics'
        AREA_CHARACTERISTICS = 10704, 'Area characteristics'
        AFFECTED_GROUP_CHARACTERISTICS = 10705, 'Affected group characteristics'
        # -- Conclusion
        # -- -- CONTEXT - INTRODUCTION
        # -- -- CASUALTIES - CROSS
        # -- Market
        # -- -- CONTEXT - INTRODUCTION
        FOOD = 10901, 'Food'
        WASH = 10902, 'Wash'
        SHELTER_AND_DOMESTIC_ITEMS = 10903, 'Shelter and domestic items'

        # Matrix 2D (Sub-ROWS) - Sub-Pillar
        # -- Impact
        DRIVERS = 20101, 'Drivers'
        IMPACT_ON_PEOPLE = 20102, 'Impact on people'
        IMPACT_ON_SYSTEMS_SERVICES_AND_NETWORKS = 20103, 'Impact on systems, services and networks'
        NUMBER_OF_PEOPLE_AFFECTED = 20104, 'Number of people affected'
        # -- Humanitarian condition
        LIVING_STANDARDS = 20201, 'Living standards'
        COPING_MECHANISMS = 20202, 'Coping mechanisms'
        PHYSICAL_AND_MENTAL_WELL_BEING = 20203, 'Physical and mental well being'
        NUMBER_OF_PEOPLE_IN_NEED = 20204, 'Number of people in need'
        # -- At Risk
        PEOPLE_AT_RISK = 20301, 'People at risk'
        NUMBER_OF_PEOPLE_AT_RISK = 20302, 'Number of people at risk'
        # -- PRIORITIES_AND_PREFERENCES
        PRIORITY_NEEDS = 20401, 'Priority needs'
        PRIORITY_INTERVENTIONS = 20402, 'Priority interventions'
        # -- Capacities and response
        GOVERNMENT_AND_LOCAL_AUTHORITIES = 20501, 'Government and local authorities'
        INTERNATIONAL_ORGANIZATIONS = 20502, 'International organizations'
        NATIONAL_AND_LOCAL_ORGANIZATIONS = 20503, 'National and local organizations'
        RED_CROSS_RED_CRESCENT = 20504, 'Red cross Red Crescent'
        HUMANITARIAN_COORDINATION = 20505, 'Humanitarian coordination'
        PEOPLE_REACHED_AND_RESPONSE_GAPS = 20506, 'People reached and response gaps'

    class Category3(models.IntegerChoices):
        # MATRIX 2D (SUB-COLUMNS) - Sector
        INTER_SECTOR = 1001, 'Inter sector'
        HEALTH = 1002, 'Health'
        WASH = 1003, 'WASH'
        SHELTER = 1004, 'Shelter'
        FOOD_SECURITY = 1005, 'Food security'
        LIVELIHOODS = 1006, 'Livelihoods'
        NUTRITION = 1007, 'Nutrition'
        EDUCATION = 1008, 'Education'
        PROTECTION = 1009, 'Protection'
        AGRICULTURE = 1010, 'Agriculture'
        LOGISTIC = 1011, 'Logistic'

    class Category4(models.IntegerChoices):
        # MATRIX 2D (SUB-COLUMNS) - Sub Sector
        # -- INTER_SECTOR
        INTRODUCTION = 10101, 'Introduction'
        CROSS = 10102, 'Cross'
        # -- HEALTH
        # -- -- INTER_SECTOR - INTRODUCTION
        # -- -- INTER_SECTOR - CROSS
        HEALTH_CARE = 10201, 'Health care'
        HEALTH_STATUS = 10202, 'Health status'
        # -- WASH
        # -- -- INTER_SECTOR - INTRODUCTION
        # -- -- INTER_SECTOR - CROSS
        WATER_SUPPLY = 10301, 'Water supply'
        SANITATION = 10302, 'Sanitation'
        SOLID_WASTE_MANAGEMENT = 10303, 'Solid waste management'
        HYGIENE = 10304, 'Hygiene'
        WASH_IN_SCHOOLS = 10305, 'WASH in schools'
        WASH_IN_HEALTH_CARE_FACILITIES = 10306, 'WASH in health care facilities'
        VECTOR_CONTROL = 10307, 'Vector control'
        # -- SHELTER
        # -- -- INTER_SECTOR - INTRODUCTION
        # -- -- INTER_SECTOR - CROSS
        DWELLING_ENVELOPE = 10401, 'Dwelling envelope'
        DOMESTIC_LIVING_SPACE = 10402, 'Domestic living space'
        NON_FOOD_HOUSEHOLD_ITEMS = 10403, 'Non-food household items'
        HOUSING_LAND_AND_PROPERTY_HLP = 10404, 'Housing, Land and Property (HLP)'
        SETTLEMENT = 10405, 'Settlement'
        # -- FOOD_SECURITY
        # -- -- INTER_SECTOR - INTRODUCTION
        # -- -- INTER_SECTOR - CROSS
        FOOD_COMMODITIES = 10501, 'Food commodities'
        NON_FOOD_ITEMS = 10502, 'Non Food Items'
        # -- LIVELIHOODS
        # -- -- INTER_SECTOR - INTRODUCTION
        # -- -- INTER_SECTOR - CROSS
        INCOME = 10601, 'Income'
        CASH = 10602, 'Cash'
        # -- NUTRITION
        # -- -- INTER_SECTOR - INTRODUCTION
        # -- -- INTER_SECTOR - CROSS
        NUTRITION_STATUS = 10701, 'Nutrition status'
        NUTRITION_SERVICES = 10702, 'Nutrition services'
        # -- EDUCATION
        # -- -- INTER_SECTOR - INTRODUCTION
        PROVISION = 10801, 'Provision'
        LEARNING_ENVIRONMENT = 10802, 'Learning environment'
        TEACHING_AND_LEARNING = 10803, 'Teaching and learning'
        TEACHERS_AND_OTHER_EDUCATION_PERSONNEL = 10804, 'Teachers and other education personnel'
        EDUCATION_POLICY = 10805, 'Education policy'
        # -- PROTECTION
        # -- -- INTER_SECTOR - INTRODUCTION
        # -- -- INTER_SECTOR - CROSS
        DOCUMENTATION = 10901, 'Documentation'
        HUMAN_CIVIL_AND_POLITICAL_RIGHTS = 10902, 'Human, civil and political rights'
        JUSTICE_AND_RULE_OF_LAW = 10903, 'Justice and rule of law'
        PHYSICAL_SAFETY_AND_SECURITY = 10904, 'Physical safety and security'
        FREEDOM_OF_MOVEMENT = 10905, 'Freedom of movement'
        CHILD_PROTECTION = 10906, 'Child Protection'
        SEXUAL_AND_GENDER_BASED_VIOLENCE = 10907, 'Sexual and Gender-Based Violence'
        # -- -- SHELTER - HOUSING_LAND_AND_PROPERTY_HLP
        MINES_UXOS_AND_IEDS = 10908, 'Mines, UXOS and IEDs'
        # -- AGRICULTURE
        # -- -- INTER_SECTOR - INTRODUCTION
        # -- -- INTER_SECTOR - CROSS
        PRODUCTION = 11001, 'Production'
        AGRICULTURAL_INPUTS = 11002, 'Agricultural inputs'
        AGRICULTURAL_INFRASTRUCTURE = 11003, 'Agricultural infrastructure'
        NATURAL_RESOURCE_MANAGEMENT = 11004, 'Natural resource management'
        # -- LOGISTIC
        # -- -- INTER_SECTOR - INTRODUCTION
        # -- -- INTER_SECTOR - CROSS
        TRANSPORT = 11101, 'Transport'
        INFORMATION_AND_COMMUNICATION_TECHNOLOGIES_ICT = 11102, 'Information and communication technologies (ICT)'
        ENERGY = 11103, 'Energy'

    TYPE_CATEGORY_MAP = {
        Type.MATRIX_1D: {
            Category1.CONTEXT: {
                Category2.INTRODUCTION,
                Category2.POLITICS,
                Category2.ECONOMICS,
                Category2.ENVIRONMENT,
                Category2.SOCIO_CULTURAL,
                Category2.DEMOGRAPHICS,
                Category2.SECURITY_AND_STABILITY,
            },
            Category1.SHOCKS_AND_EVENTS: {
                Category2.INTRODUCTION,
                Category2.TYPE_AND_CHARACTERISTICS,
                Category2.AGGRAVATING_FACTORS,
                Category2.MITIGATING_FACTORS,
                Category2.THREATS_AND_HAZARDS,
            },
            Category1.DISPLACEMENT: {
                Category2.INTRODUCTION_PEOPLE_ARRIVING,
                Category2.INTRODUCTION_PEOPLE_LEAVING,
                Category2.TYPE_AND_CHARACTERISTICS,
                Category2.PULL_FACTORS,
                Category2.PUSH_FACTORS,
                Category2.INTENTIONS,
                Category2.LOCAL_INTEGRATION,
            },
            Category1.CASUALTIES: {
                Category2.INTRODUCTION,
                Category2.CROSS,
                Category2.DEAD,
                Category2.INJURED,
                Category2.MISSING,
            },
            Category1.INFORMATION_AND_COMMUNICATION: {
                Category2.INTRODUCTION,
                Category2.CROSS,
                Category2.COMMUNICATION_SOURCES_AND_MEANS,
                Category2.CHALLENGES_AND_BARRIERS,
                Category2.KNOWLEDGE_AND_INFORMATION_GAPS_POPULATION,
                Category2.KNOWLEDGE_AND_INFORMATION_GAPS_HUMANITARIANS,
            },
            Category1.HUMANITARIAN_ACCESS: {
                Category2.INTRODUCTION_HUMANITARIAN_ACTORS_BARRIERS,
                Category2.INTRODUCTION_PEOPLE_AFFECTED_BARRIERS,
                Category2.POPULATION_TO_RELIEF,
                Category2.RELIEF_TO_POPULATION,
                Category2.PHYSICAL_AND_SECURITY_CONSTRAINTS,
                Category2.PEOPLE_FACING_HUMANITARIAN_ACCESS_CONSTRAINT_HUMANITARIAN_ACCESS_GAPS,
            },
            Category1.INTRODUCTION: {
                Category2.INTRODUCTION,
                Category2.QUESTIONNAIRE_CHARACTERISTICS,
                Category2.ENUMERATOR_CHARACTERISTICS,
                Category2.RESPONDENT_CHARACTERISTICS,
                Category2.AREA_CHARACTERISTICS,
                Category2.AFFECTED_GROUP_CHARACTERISTICS,
            },
            Category1.CONCLUSION: {
                Category2.INTRODUCTION,
                Category2.CROSS,
            },
            Category1.MARKET: {
                Category2.INTRODUCTION,
                Category2.FOOD,
                Category2.WASH,
                Category2.SHELTER_AND_DOMESTIC_ITEMS,
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
                Category1.PRIORITIES_AND_PREFERENCES: {
                    Category2.PRIORITY_NEEDS,
                    Category2.PRIORITY_INTERVENTIONS,
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
                Category3.INTER_SECTOR: {
                    Category4.INTRODUCTION,
                    Category4.CROSS,
                },
                Category3.HEALTH: {
                    Category4.INTRODUCTION,
                    Category4.CROSS,
                    Category4.HEALTH_CARE,
                    Category4.HEALTH_STATUS,
                },
                Category3.WASH: {
                    Category4.INTRODUCTION,
                    Category4.CROSS,
                    Category4.WATER_SUPPLY,
                    Category4.SANITATION,
                    Category4.SOLID_WASTE_MANAGEMENT,
                    Category4.HYGIENE,
                    Category4.WASH_IN_SCHOOLS,
                    Category4.WASH_IN_HEALTH_CARE_FACILITIES,
                    Category4.VECTOR_CONTROL,
                },
                Category3.SHELTER: {
                    Category4.INTRODUCTION,
                    Category4.CROSS,
                    Category4.DWELLING_ENVELOPE,
                    Category4.DOMESTIC_LIVING_SPACE,
                    Category4.NON_FOOD_HOUSEHOLD_ITEMS,
                    Category4.HOUSING_LAND_AND_PROPERTY_HLP,
                    Category4.SETTLEMENT,
                },
                Category3.FOOD_SECURITY: {
                    Category4.INTRODUCTION,
                    Category4.CROSS,
                    Category4.FOOD_COMMODITIES,
                    Category4.NON_FOOD_ITEMS,
                },
                Category3.LIVELIHOODS: {
                    Category4.INTRODUCTION,
                    Category4.CROSS,
                    Category4.INCOME,
                    Category4.CASH,
                },
                Category3.NUTRITION: {
                    Category4.INTRODUCTION,
                    Category4.CROSS,
                    Category4.NUTRITION_STATUS,
                    Category4.NUTRITION_SERVICES,
                },
                Category3.EDUCATION: {
                    Category4.INTRODUCTION,
                    Category4.PROVISION,
                    Category4.LEARNING_ENVIRONMENT,
                    Category4.TEACHING_AND_LEARNING,
                    Category4.TEACHERS_AND_OTHER_EDUCATION_PERSONNEL,
                    Category4.EDUCATION_POLICY,
                },
                Category3.PROTECTION: {
                    Category4.INTRODUCTION,
                    Category4.CROSS,
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
                    Category4.INTRODUCTION,
                    Category4.CROSS,
                    Category4.PRODUCTION,
                    Category4.AGRICULTURAL_INPUTS,
                    Category4.AGRICULTURAL_INFRASTRUCTURE,
                    Category4.NATURAL_RESOURCE_MANAGEMENT,
                },
                Category3.LOGISTIC: {
                    Category4.INTRODUCTION,
                    Category4.CROSS,
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
